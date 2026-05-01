from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import pandas as pd
import requests

URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "edat_lfse_24?format=JSON&lang=EN&time=2022&time=2023"
)
RAW_PATH = Path("data/raw/eurostat/edat_lfse_24_ALL.json")
CSV_PATH = Path("data/raw/eurostat/eurostat_employment_full.csv")
ISCED_F_TO_FAMILY = {
    "F00": "general_studies", "F01": "education", "F02": "creative_arts", "F03": "humanities",
    "F04": "social_sciences", "F05": "communications", "F06": "business", "F07": "law",
    "F08": "biological_sciences", "F09": "physical_sciences", "F10": "mathematics",
    "F11": "computer_science", "F14": "engineering", "F15": "engineering", "F16": "architecture",
    "F21": "agriculture", "F22": "agriculture", "F31": "medicine", "F32": "healthcare",
    "F38": "social_sciences", "F41": "education", "F58": "computer_science",
    "F84": "hospitality", "F85": "engineering", "F86": "environmental_sciences",
}
COUNTRIES = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "HR": "Croatia", "CY": "Cyprus",
    "CZ": "Czechia", "DK": "Denmark", "EE": "Estonia", "FI": "Finland", "FR": "France",
    "DE": "Germany", "GR": "Greece", "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
    "LV": "Latvia", "LT": "Lithuania", "LU": "Luxembourg", "MT": "Malta", "NL": "Netherlands",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SK": "Slovakia", "SI": "Slovenia",
    "ES": "Spain", "SE": "Sweden", "UK": "United Kingdom", "NO": "Norway", "CH": "Switzerland",
}


def _pick_key(payload: dict, options: tuple[str, ...]) -> str | None:
    for key in payload["id"]:
        if key in options or any(opt in key.lower() for opt in options):
            return key
    return None


def _flat_index(coords: list[int], sizes: list[int]) -> int:
    index = 0
    for pos, coord in enumerate(coords):
        stride = 1
        for next_size in sizes[pos + 1:]:
            stride *= next_size
        index += coord * stride
    return index


def main() -> None:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = requests.get(URL, timeout=120).json()
    RAW_PATH.write_text(json.dumps(payload), encoding="utf-8")

    geo_key = _pick_key(payload, ("geo",))
    field_key = _pick_key(payload, ("field", "foet", "c_foet"))
    isced_key = _pick_key(payload, ("isced11",))
    sex_key = _pick_key(payload, ("sex",))
    time_key = _pick_key(payload, ("time",))
    status_key = _pick_key(payload, ("wstatus", "labstat", "status"))
    unit_key = _pick_key(payload, ("unit",))
    ids, sizes, values = payload["id"], payload["size"], payload.get("value", {})
    categories = {key: payload["dimension"][key]["category"]["index"] for key in ids}
    records: list[dict[str, object]] = []

    for combo in product(*[range(size) for size in sizes]):
        coords = dict(zip(ids, combo))
        geo_code = next(code for code, idx in categories[geo_key].items() if idx == coords[geo_key])
        if geo_code not in COUNTRIES:
            continue
        sex_code = next(code for code, idx in categories[sex_key].items() if idx == coords[sex_key]) if sex_key else "T"
        if sex_code != "T":
            continue
        isced_code = next(code for code, idx in categories[isced_key].items() if idx == coords[isced_key])
        if "ED5-8" not in isced_code and "5-8" not in isced_code:
            continue
        if status_key:
            status_code = next(code for code, idx in categories[status_key].items() if idx == coords[status_key])
            if status_code != "EMP":
                continue
        if unit_key:
            unit_code = next(code for code, idx in categories[unit_key].items() if idx == coords[unit_key])
            if unit_code != "PC":
                continue
        field_code = (
            next(code for code, idx in categories[field_key].items() if idx == coords[field_key])
            if field_key
            else "F00"
        )
        year = int(next(code for code, idx in categories[time_key].items() if idx == coords[time_key]))
        flat = _flat_index(list(combo), sizes)
        value = values.get(str(flat))
        if value is None:
            continue
        duration_code = next(code for code, idx in categories["duration"].items() if idx == coords["duration"])
        age_code = next(code for code, idx in categories["age"].items() if idx == coords["age"])
        if duration_code != "TOTAL" or age_code != "Y20-34":
            continue
        records.append(
            {
                "country_code": geo_code,
                "isced_field": field_code,
                "employment_rate": float(value) / 100.0,
                "year": year,
            }
        )

    frame = pd.DataFrame(records)
    frame = frame.sort_values("year").groupby(["country_code", "isced_field"], as_index=False).tail(1)
    frame["program_family"] = frame["isced_field"].map(ISCED_F_TO_FAMILY).fillna("general_studies")
    frame["country"] = frame["country_code"].map(COUNTRIES)
    output = frame.groupby(["program_family", "country"], as_index=False)["employment_rate"].mean()
    output["source"] = "Eurostat_edat_lfse_24"
    output.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(output)} Eurostat rows to {CSV_PATH}")


if __name__ == "__main__":
    main()
