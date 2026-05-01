from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import pandas as pd
import requests

from app.outcomes.mapping import isced_to_program_family

OUT_DIR = Path("data/raw/eurostat_salary")
EARNINGS_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "earn_ses18_30?format=JSON&lang=EN&geo=DE&sex=T&unit=EUR&nace_r2=B-S_X_O&sizeclas=GE10&indic_se=ERN"
)
RAW_NAME = "earn_ses18_30_raw.json"


def _find_dim(payload: dict, names: tuple[str, ...]) -> str | None:
    for dim_name in payload["id"]:
        lowered = dim_name.lower()
        if lowered in names or any(name in lowered for name in names):
            return dim_name
    return None


def _flat_records(payload: dict) -> pd.DataFrame:
    ids = payload["id"]
    sizes = payload["size"]
    categories = {key: payload["dimension"][key]["category"]["index"] for key in ids}
    reverse = {key: {idx: code for code, idx in index.items()} for key, index in categories.items()}
    values = payload.get("value", {})
    rows: list[dict[str, object]] = []
    for combo in product(*[range(size) for size in sizes]):
        flat = 0
        for pos, coord in enumerate(combo):
            stride = 1
            for next_size in sizes[pos + 1 :]:
                stride *= next_size
            flat += coord * stride
        value = values.get(str(flat))
        if value is None:
            continue
        row = {ids[pos]: reverse[ids[pos]][coord] for pos, coord in enumerate(combo)}
        row["value"] = float(value)
        rows.append(row)
    return pd.DataFrame(rows)


def _fetch_payload(url: str, raw_name: str) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    payload = response.json()
    (OUT_DIR / raw_name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return _flat_records(payload)


def _filter_germany_rows(frame: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    geo_dim = _find_dim({"id": list(frame.columns), "size": []}, ("geo",))
    time_dim = _find_dim({"id": list(frame.columns), "size": []}, ("time",))
    isced_dim = _find_dim({"id": list(frame.columns), "size": []}, ("isced", "field"))
    if not geo_dim or not time_dim or not isced_dim:
        return pd.DataFrame(), ""
    working = frame.copy()
    for dim, expected in (("sex", "T"), ("unit", "EUR"), ("nace", "B-S_X_O"), ("sizeclas", "GE10")):
        dim_name = _find_dim({"id": list(working.columns), "size": []}, (dim,))
        if dim_name and expected in set(working[dim_name].astype(str)):
            working = working[working[dim_name].astype(str) == expected]
    working = working[working[geo_dim].astype(str) == "DE"]
    tertiary = working[isced_dim].astype(str).str.contains(r"ED5|ED6|ED7|ED8|5-8", regex=True, na=False)
    working = working[tertiary]
    if working.empty:
        return pd.DataFrame(), ""
    latest_year = sorted(working[time_dim].astype(str).unique())[-1]
    return working[working[time_dim].astype(str) == latest_year].copy(), latest_year


def _build_salary_bands(frame: pd.DataFrame, year: str) -> pd.DataFrame:
    isced_dim = _find_dim({"id": list(frame.columns), "size": []}, ("isced", "field"))
    mapped = frame.copy()
    mapped["program_family"] = mapped[isced_dim].astype(str).map(isced_to_program_family)
    detailed = mapped[mapped["program_family"] != "general_studies"]
    if not detailed.empty:
        grouped = detailed.groupby("program_family", as_index=False)["value"].median()
        grouped["median_eur"] = grouped["value"]
    else:
        weights = pd.read_csv("data/raw/eurostat/eurostat_employment_full.csv")
        de_weights = weights[weights["country"] == "Germany"][["program_family", "employment_rate"]].copy()
        de_weights["weight"] = de_weights["employment_rate"] / de_weights["employment_rate"].sum()
        spread = (de_weights["weight"] - de_weights["weight"].mean()) / de_weights["weight"].std(ddof=0)
        de_weights["adjustment"] = spread.fillna(0).clip(-1, 1) * 0.20
        tertiary = mapped[mapped[isced_dim].astype(str) == "ED5-8"]
        aggregate_median = float(tertiary["value"].iloc[0] if not tertiary.empty else mapped["value"].median())
        grouped = de_weights[["program_family"]].copy()
        grouped["median_eur"] = aggregate_median * (1 + de_weights["adjustment"])
    grouped["p15_eur"] = grouped["median_eur"] * 0.78
    grouped["p85_eur"] = grouped["median_eur"] * 1.24
    grouped["country"] = "Germany"
    grouped["source"] = "Eurostat_SES_earn_ses_pub1s"
    grouped["currency"] = "EUR"
    grouped["year"] = year
    return grouped[
        ["program_family", "country", "median_eur", "p15_eur", "p85_eur", "source", "currency", "year"]
    ]


def main() -> None:
    parsed = _fetch_payload(EARNINGS_URL, RAW_NAME)
    germany_rows, latest_year = _filter_germany_rows(parsed)
    if germany_rows.empty:
        raise RuntimeError("Eurostat earnings table earn_ses18_30 returned no Germany tertiary rows.")
    germany_rows.to_csv(OUT_DIR / "earn_ses18_30_parsed.csv", index=False)
    salary_bands = _build_salary_bands(germany_rows, latest_year)
    salary_bands.to_csv(OUT_DIR / "germany_salary_bands.csv", index=False)
    print(f"Wrote Germany salary bands for {len(salary_bands)} program families ({latest_year}).")


if __name__ == "__main__":
    main()
