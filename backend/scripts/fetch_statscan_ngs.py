from __future__ import annotations
import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

OUT_DIR = Path("data/raw/statscan")
NGS_URL = "https://www150.statcan.gc.ca/n1/pub/81m0011x/2024001/CSV_PUMF-eng.zip"
ALT_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/dtbl!download/tabular?pid=3710012201"
TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/dtbl!download/tabular?pid=3710011501"
ACTIVE_TABLE_URL = "https://www150.statcan.gc.ca/n1/tbl/csv/37100281-eng.zip"
CANADA_OECD_EAG = {
    "computer_science": 0.88,
    "engineering": 0.88,
    "business": 0.85,
    "healthcare": 0.91,
    "biological_sciences": 0.79,
    "social_sciences": 0.79,
    "humanities": 0.72,
    "education": 0.83,
    "law": 0.85,
    "mathematics": 0.88,
    "architecture": 0.82,
    "creative_arts": 0.72,
    "environmental_sciences": 0.80,
    "agriculture": 0.78,
    "communications": 0.72,
    "general_studies": 0.81,
}
CIP_TO_FAMILY = {
    "01": "agriculture",
    "03": "environmental_sciences",
    "04": "architecture",
    "09": "communications",
    "11": "computer_science",
    "13": "education",
    "14": "engineering",
    "15": "engineering",
    "16": "humanities",
    "22": "law",
    "26": "biological_sciences",
    "27": "mathematics",
    "30": "general_studies",
    "40": "physical_sciences",
    "42": "psychology",
    "44": "social_sciences",
    "45": "social_sciences",
    "50": "creative_arts",
    "51": "healthcare",
    "52": "business",
}
BROAD_FIELD_TO_FAMILIES = {
    "Total, field of study": ["general_studies"], "Education [1]": ["education"],
    "Visual and performing arts, and communications technologies [2]": ["creative_arts", "communications"], "Humanities [3]": ["humanities"],
    "Social and behavioural sciences and law [4]": ["social_sciences", "law"], "Business, management and public administration [5]": ["business"],
    "Physical and life sciences and technologies [6]": ["physical_sciences", "biological_sciences"], "Mathematics, computer and information sciences [7]": ["mathematics", "computer_science"],
    "Architecture, engineering, and related trades [8]": ["architecture", "engineering"], "Agriculture, natural resources and conservation [9]": ["agriculture", "environmental_sciences"],
    "Health and related fields [10]": ["healthcare", "medicine"],
}
def _download_zip(url: str, out_dir: Path) -> bool:
    response = requests.get(url, timeout=120, stream=True)
    if response.status_code != 200:
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            archive.extractall(out_dir)
    except zipfile.BadZipFile:
        return False
    return True
def _write_oecd_fallback() -> Path:
    frame = pd.DataFrame(
        [
            {
                "program_family": family,
                "country": "Canada",
                "employment_rate": rate,
                "source": "OECD_EAG_2023_Canada",
            }
            for family, rate in CANADA_OECD_EAG.items()
        ]
    )
    path = OUT_DIR / "canada_placement_oecd_eag.csv"
    frame.to_csv(path, index=False)
    return path
def _download_statscan_table() -> pd.DataFrame:
    response = requests.get(ACTIVE_TABLE_URL, timeout=180)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(OUT_DIR / "ngs_table_37100281")
        with archive.open("37100281.csv") as handle:
            return pd.read_csv(handle, dtype=str, low_memory=False, encoding="utf-8-sig")
def _expand_program_rows(field_label: str, value: float) -> list[dict[str, object]]:
    families = BROAD_FIELD_TO_FAMILIES.get(field_label, [])
    return [{"program_family": family, "value": value} for family in families]
def _build_from_statscan_table() -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = _download_statscan_table()
    year = "2020" if "2020" in set(frame["REF_DATE"].astype(str)) else max(frame["REF_DATE"].astype(str))
    base = frame[
        (frame["REF_DATE"].astype(str) == year)
        & (frame["GEO"] == "Canada")
        & (frame["Educational qualification"] == "Undergraduate degree")
        & (frame["Gender"] == "Total, gender")
        & (frame["Age group"] == "15 to 64 years")
        & (frame["Status of student in Canada"] == "Canadian and international students")
        & (frame["Field of study"].isin(BROAD_FIELD_TO_FAMILIES))
    ].copy()
    base["VALUE"] = pd.to_numeric(base["VALUE"], errors="coerce")
    counts = base[base["Graduate statistics"] == "Number of graduates"]
    all_grads = counts[counts["Characteristics after graduation"] == "All graduates"][
        ["Field of study", "VALUE"]
    ].rename(columns={"VALUE": "all_graduates"})
    employed = counts[counts["Characteristics after graduation"] == "Graduates reporting employment income"][
        ["Field of study", "VALUE"]
    ].rename(columns={"VALUE": "employed_graduates"})
    placement = all_grads.merge(employed, on="Field of study", how="inner")
    placement["employment_rate"] = placement["employed_graduates"] / placement["all_graduates"]

    placement_rows: list[dict[str, object]] = []
    for _, row in placement.iterrows():
        for expanded in _expand_program_rows(row["Field of study"], float(row["employment_rate"])):
            placement_rows.append(
                {
                    "program_family": expanded["program_family"],
                    "country": "Canada",
                    "employment_rate": expanded["value"],
                    "source": "StatsCan_NGS_2020",
                }
            )

    salary = base[
        (base["Graduate statistics"] == "Median employment income")
        & (base["Characteristics after graduation"] == "Graduates reporting wages, salaries and commissions only")
    ][["Field of study", "VALUE"]].rename(columns={"VALUE": "salary_median"})
    salary_rows: list[dict[str, object]] = []
    for _, row in salary.iterrows():
        if pd.isna(row["salary_median"]):
            continue
        for expanded in _expand_program_rows(row["Field of study"], float(row["salary_median"])):
            salary_rows.append(
                {
                    "program_family": expanded["program_family"],
                    "country": "Canada",
                    "salary_median": expanded["value"],
                    "currency": "CAD",
                    "source": "StatsCan_NGS_2020",
                }
            )

    return pd.DataFrame(placement_rows), pd.DataFrame(salary_rows)
def _parse_ngs_csv(csv_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    ngs = pd.read_csv(csv_path, dtype=str, low_memory=False)
    fld_col = next((c for c in ngs.columns if "FLD" in c.upper()), None)
    emp_col = next((c for c in ngs.columns if "EMP" in c.upper()), None)
    inc_col = next((c for c in ngs.columns if "INCM" in c.upper() or "INC" in c.upper()), None)
    if not all([fld_col, emp_col, inc_col]):
        raise RuntimeError(f"Missing required NGS columns in {csv_path.name}.")
    working = ngs[[fld_col, emp_col, inc_col]].copy()
    working["cip2"] = working[fld_col].astype(str).str[:2].str.zfill(2)
    working["program_family"] = working["cip2"].map(CIP_TO_FAMILY)
    working = working[working["program_family"].notna()].copy()
    working["employment_rate"] = pd.to_numeric(working[emp_col], errors="coerce")
    working["income"] = pd.to_numeric(working[inc_col], errors="coerce")
    working = working.dropna(subset=["employment_rate", "income"])
    emp_rates = working.groupby("program_family", as_index=False)["employment_rate"].mean()
    emp_rates["country"] = "Canada"
    emp_rates["source"] = "StatsCan_NGS_2020"
    salary = working.groupby("program_family")["income"].quantile([0.15, 0.50, 0.85]).unstack().reset_index()
    salary.columns = ["program_family", "salary_p15", "salary_median", "salary_p85"]
    salary["country"] = "Canada"
    salary["currency"] = "CAD"
    salary["source"] = "StatsCan_NGS_2020"
    return emp_rates, salary
def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pumf_dir = OUT_DIR / "ngs_pumf_raw"
    aggregate_dir = OUT_DIR / "ngs_aggregate_raw"
    table_dir = OUT_DIR / "ngs_3710011501"
    ok = _download_zip(NGS_URL, pumf_dir)
    if not ok: ok = _download_zip(ALT_URL, aggregate_dir)
    if not ok: ok = _download_zip(TABLE_URL, table_dir)
    csv_candidates = list(pumf_dir.glob("*.csv")) + list(pumf_dir.glob("**/*.csv"))
    if csv_candidates:
        main_csv = max(csv_candidates, key=lambda path: path.stat().st_size)
        placement, salary = _parse_ngs_csv(main_csv)
        placement.to_csv(OUT_DIR / "canada_placement_ngs.csv", index=False)
        salary.to_csv(OUT_DIR / "canada_salary_ngs.csv", index=False)
        print(f"Wrote Canada placement ({len(placement)}) and salary ({len(salary)}) rows from {main_csv.name}.")
        return
    try:
        placement, salary = _build_from_statscan_table()
    except Exception:
        placement = pd.DataFrame()
        salary = pd.DataFrame()
    if not placement.empty:
        placement.to_csv(OUT_DIR / "canada_placement_ngs.csv", index=False)
    if not salary.empty:
        salary.to_csv(OUT_DIR / "canada_salary_ngs.csv", index=False)
    if not placement.empty and not salary.empty:
        print(f"Wrote Canada placement ({len(placement)}) and salary ({len(salary)}) rows from StatsCan table 37100281.")
        return
    if _write_oecd_fallback().exists():
        print("StatsCan downloads did not expose a usable PUMF CSV; wrote OECD placement fallback.")
        return
    raise RuntimeError("StatsCan download paths failed and OECD fallback CSV could not be produced.")
if __name__ == "__main__":
    main()
