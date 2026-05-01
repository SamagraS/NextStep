from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pdfplumber
import requests

RAW_DIR = Path("data/raw/nirf")
NIRF_TARGETS = [
    ("Engineering", "IR-E-U-0306"), ("Engineering", "IR-E-U-0452"), ("Engineering", "IR-E-U-0508"),
    ("Engineering", "IR-E-U-0419"), ("Engineering", "IR-E-U-0560"), ("Engineering", "IR-E-U-0014"),
    ("Engineering", "IR-E-U-0436"), ("Engineering", "IR-E-U-0574"), ("Engineering", "IR-E-U-0232"),
    ("Engineering", "IR-E-U-0101"), ("Engineering", "IR-E-U-0061"), ("Engineering", "IR-E-U-0099"),
    ("Overall", "IR-O-U-0042"), ("Overall", "IR-O-U-0091"), ("Overall", "IR-O-U-0130"),
    ("Overall", "IR-O-U-0376"), ("Overall", "IR-O-U-0150"), ("Overall", "IR-O-U-0200"),
    ("Overall", "IR-O-U-0300"), ("Overall", "IR-O-U-0088"),
]
NAME_HINTS = {
    "IR-E-U-0306": "IIT Bombay", "IR-E-U-0452": "IIT Delhi", "IR-E-U-0508": "IIT Madras",
    "IR-E-U-0419": "IIT Kanpur", "IR-E-U-0560": "IIT Roorkee", "IR-E-U-0014": "IIIT Hyderabad",
    "IR-E-U-0436": "NIT Trichy", "IR-E-U-0574": "NIT Warangal", "IR-E-U-0232": "BITS Pilani",
    "IR-E-U-0101": "VIT Vellore", "IR-E-U-0061": "Manipal Institute", "IR-E-U-0099": "SRM Institute",
    "IR-O-U-0042": "University of Hyderabad", "IR-O-U-0091": "Jadavpur University", "IR-O-U-0130": "Amity University",
    "IR-O-U-0376": "Mid-range University", "IR-O-U-0150": "Symbiosis", "IR-O-U-0200": "Lovely Professional University",
    "IR-O-U-0300": "Chandigarh University", "IR-O-U-0088": "Anna University",
}


def _tier(name: str) -> int:
    upper = name.upper()
    if any(token in upper for token in ("IIT", "IIIT", "IISC")):
        return 1
    if any(token in upper for token in ("NIT", "BITS")):
        return 2
    return 3


def _salary(text: str) -> float | None:
    matches = [int(m.replace(",", "")) for m in re.findall(r"(\d[\d,]{4,})", text)]
    return float(matches[0]) if matches else None


def _parse_pdf(path: Path, nirf_id: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table:
                    continue
                header = [str(cell or "").replace("\n", " ").strip() for cell in table[0]]
                lower = " ".join(header).lower()
                if "median salary" not in lower or "placed" not in lower:
                    continue
                grad_idx = next((i for i, cell in enumerate(header) if "graduating" in cell.lower()), None)
                placed_idx = next((i for i, cell in enumerate(header) if cell.lower().startswith("no. of students placed") or cell.lower() == "no. of students placed"), None)
                salary_idx = next((i for i, cell in enumerate(header) if "median salary" in cell.lower()), None)
                year_idx = next((i for i, cell in enumerate(header) if "academic year" in cell.lower()), 0)
                if None in (grad_idx, placed_idx, salary_idx):
                    continue
                for row in table[1:]:
                    cells = [str(cell or "").replace("\n", " ").strip() for cell in row]
                    if max(grad_idx, placed_idx, salary_idx, year_idx) >= len(cells):
                        continue
                    year_match = re.search(r"(20\d{2})", cells[year_idx])
                    grad = cells[grad_idx].replace(",", "")
                    placed = cells[placed_idx].replace(",", "")
                    salary = _salary(cells[salary_idx])
                    if not year_match or not grad.isdigit() or not placed.isdigit() or salary is None:
                        continue
                    graduating, placed_n = int(grad), int(placed)
                    if graduating <= 0:
                        continue
                    rows.append(
                        {
                            "nirf_id": nirf_id,
                            "year": int(year_match.group(1)),
                            "institution_tier": _tier(NAME_HINTS.get(nirf_id, nirf_id)),
                            "placement_rate": min(1.0, placed_n / graduating),
                            "median_salary_inr": salary,
                        }
                    )
    return rows


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for category, nirf_id in NIRF_TARGETS:
        path = RAW_DIR / f"{category}_{nirf_id}.pdf"
        if not path.exists():
            categories = [category] + [alt for alt in ("Engineering", "Overall") if alt != category]
            downloaded = False
            last_error: Exception | None = None
            for current_category in categories:
                url = f"https://www.nirfindia.org/nirfpdfcdn/2024/pdf/{current_category}/{nirf_id}.pdf"
                try:
                    response = requests.get(url, timeout=120)
                    response.raise_for_status()
                    path.write_bytes(response.content)
                    downloaded = True
                    break
                except Exception as exc:
                    last_error = exc
            if not downloaded:
                print(f"skip {nirf_id}: {last_error}")
                continue
        records.extend(_parse_pdf(path, nirf_id))

    frame = pd.DataFrame(records)
    summary = frame.groupby(["institution_tier", "year"]).agg(
        placement_rate=("placement_rate", "median"),
        median_salary_inr=("median_salary_inr", "median"),
        n_institutions=("nirf_id", "nunique"),
    ).reset_index()
    summary.to_csv(RAW_DIR / "nirf_aggregated.csv", index=False)
    print(f"Saved {len(summary)} aggregated NIRF rows to {RAW_DIR / 'nirf_aggregated.csv'}")


if __name__ == "__main__":
    main()
