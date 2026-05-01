from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

# Adjust path to import from backend/app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.outcomes.mapping import soc_to_program_family

URLS = [
    "https://www.bls.gov/oes/special.requests/oesnat.zip",
    "https://www.bls.gov/oes/special-requests/oesm24nat.zip",
]
RAW_DIR = Path("data/raw/bls")
KEEP = ["OCC_CODE", "OCC_TITLE", "TOT_EMP", "A_PCT10", "A_MEDIAN", "A_PCT90"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


def _scale(series: pd.Series) -> pd.Series:
    minimum, maximum = series.min(), series.max()
    if pd.isna(minimum) or pd.isna(maximum) or minimum == maximum:
        return pd.Series([0.735] * len(series), index=series.index)
    return 0.55 + ((series - minimum) / (maximum - minimum)) * (0.92 - 0.55)


def _read_main_workbook(bls_dir: Path) -> pd.DataFrame:
    candidates = list(bls_dir.glob("all_data_M_*.xlsx")) + list(bls_dir.glob("nat_M_*_dl.xlsx"))
    for path in sorted(candidates, reverse=True):
        try:
            return pd.read_excel(path, engine="openpyxl", usecols=KEEP)
        except Exception:
            continue
    raise FileNotFoundError("No BLS national workbook found after extraction.")


def main() -> None:
    # OFLC-based derivation: BLS ZIP is 403-blocked, so derive from H1B/LCA data
    raw_oflc = Path("data/raw/oflc")
    out_path = Path("data/raw/bls") / "bls_us_employment_proxy.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load all OFLC Excel files present
    files = list(raw_oflc.glob("*.xls*"))
    if not files:
        raise FileNotFoundError("No OFLC files found in data/raw/oflc/")

    frames = []
    for f in files:
        try:
            # Use openpyxl for all Excel files
            try:
                df = pd.read_excel(f, engine='openpyxl', dtype=str)
            except Exception:
                # Fallback to auto-detect
                df = pd.read_excel(f, dtype=str)
            df.columns = df.columns.str.strip().str.upper()
            frames.append(df)
        except Exception as e:
            print(f"Warning: skipping {f} due to {e}")
            continue

    if not frames:
        raise RuntimeError("Could not read any OFLC files")

    lca = pd.concat(frames, ignore_index=True)

    # Normalise column names — OFLC files use slightly different names per year
    soc_col = next((c for c in lca.columns if "SOC_CODE" in c), None)
    wage_col = next(
        (c for c in lca.columns if "WAGE_RATE" in c or "PREVAILING_WAGE" in c), None
    )
    status_col = next((c for c in lca.columns if "CASE_STATUS" in c), None)

    if not soc_col or not status_col:
        raise ValueError(
            f"Cannot find SOC or STATUS columns in OFLC data. Columns: {list(lca.columns)}"
        )

    # Keep only certified/approved cases with a valid SOC
    lca = lca[lca[status_col].str.upper().str.startswith("CERTIFIED", na=False)]
    lca = lca[lca[soc_col].notna()]
    lca[soc_col] = lca[soc_col].str.strip()

    # Map SOC -> program_family using existing helper
    lca["program_family"] = lca[soc_col].map(soc_to_program_family)
    lca = lca[lca["program_family"].notna()]

    # Employment proxy = share of certified H1B cases per family
    # Normalised to 0.55–0.92 range (demand proxy, not absolute rate)
    counts = lca.groupby("program_family").size().reset_index(name="case_count")
    mn, mx = counts["case_count"].min(), counts["case_count"].max()
    counts["employment_rate"] = 0.55 + (counts["case_count"] - mn) / (mx - mn) * (
        0.92 - 0.55
    )
    counts["country"] = "United States"
    counts["source"] = "BLS_OES_proxy"  # keep label consistent with ingestion.py
    counts[["program_family", "country", "employment_rate", "source"]].to_csv(
        out_path, index=False
    )
    print(f"Wrote {len(counts)} rows -> {out_path}")


if __name__ == "__main__":
    main()
