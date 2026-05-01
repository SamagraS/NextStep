from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


try:
    import pdfplumber
except Exception:  # pragma: no cover - optional dependency
    pdfplumber = None


@dataclass(frozen=True)
class RawDatasetBundle:
    hesa_subject: pd.DataFrame
    hesa_salary: pd.DataFrame
    qilt_employment: pd.DataFrame
    qilt_salary: pd.DataFrame
    eurostat: pd.DataFrame
    eurostat_salary: pd.DataFrame
    bls_employment: pd.DataFrame
    oflc: pd.DataFrame
    nirf: pd.DataFrame
    statscan_placement: pd.DataFrame
    statscan_salary: pd.DataFrame
    world_bank: pd.DataFrame


class DatasetIngestor:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"

    def load(self) -> RawDatasetBundle:
        return RawDatasetBundle(
            hesa_subject=self._load_hesa_subject(),
            hesa_salary=self._load_hesa_salary(),
            qilt_employment=self._load_qilt_employment(),
            qilt_salary=self._load_qilt_salary(),
            eurostat=self._load_eurostat(),
            eurostat_salary=self._load_eurostat_salary(),
            bls_employment=self._load_bls_employment(),
            oflc=self._load_oflc(),
            nirf=self._load_nirf(),
            statscan_placement=self._load_statscan_placement(),
            statscan_salary=self._load_statscan_salary(),
            world_bank=self._load_world_bank(),
        )

    def load_placement_sources(self) -> list[pd.DataFrame]:
        frames: list[pd.DataFrame] = []
        eurostat_full_path = self.raw_dir / "eurostat" / "eurostat_employment_full.csv"
        if eurostat_full_path.exists():
            frames.append(pd.read_csv(eurostat_full_path))
        else:
            eurostat_dir = self.raw_dir / "eurostat"
            for path in sorted(eurostat_dir.glob("*.json")):
                payload = json.loads(path.read_text(encoding="utf-8"))
                time_labels = payload["dimension"]["time"]["category"]["label"]
                geo_labels = payload["dimension"]["geo"]["category"]["label"]
                for geo_code, geo_name in geo_labels.items():
                    for idx, year in enumerate(time_labels.keys()):
                        value = payload.get("value", {}).get(str(idx))
                        if value is None:
                            continue
                        frames.append(
                            pd.DataFrame(
                                [
                                    {
                                        "country": geo_name,
                                        "geo_code": geo_code,
                                        "year": int(year),
                                        "employment_rate": float(value) / 100.0,
                                        "dataset": payload.get("extension", {}).get("id", "EDAT_LFSE_24"),
                                    }
                                ]
                            )
                        )
        bls_path = self.raw_dir / "bls" / "bls_us_employment_proxy.csv"
        if bls_path.exists():
            frames.append(pd.read_csv(bls_path))
        return frames

    def _raw_path(self, folder: str, filename: str) -> Path:
        preferred = self.raw_dir / folder / filename
        if preferred.exists():
            return preferred
        legacy = self.data_dir / folder / filename
        return legacy

    def _read_csv_after_marker(
        self,
        path: Path,
        marker: str,
        encoding: str = "utf-8-sig",
        na_values: list[str] | None = None,
    ) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()

        rows = path.read_text(encoding=encoding).splitlines()
        start = 0
        for index, row in enumerate(rows):
            if marker in row:
                start = index
                break
        return pd.read_csv(path, skiprows=start, na_values=na_values)

    def _load_hesa_subject(self) -> pd.DataFrame:
        path = self._raw_path("hesa", "sb272-figure-10.csv")
        frame = self._read_csv_after_marker(
            path,
            '"Subject area of degree"',
            na_values=["*", "N/A", "n/a", "na", "-", "...", "c", "x"],
        )
        return frame.dropna(how="all")

    def _load_hesa_salary(self) -> pd.DataFrame:
        path = self._raw_path("hesa", "sb272-figure-13.csv")
        frame = self._read_csv_after_marker(
            path,
            '"Salary band"',
            na_values=["*", "N/A", "n/a", "na", "-", "...", "c", "x"],
        )
        return frame.dropna(how="all")

    def _load_qilt_employment(self) -> pd.DataFrame:
        path = self._raw_path("qilt", "EMP_UG_ALL_2Y_AREA.csv")
        if not path.exists():
            path = self._raw_path("qilt", "EMP_UG_ALL_2Y_AREA45.csv")
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    def _load_qilt_salary(self) -> pd.DataFrame:
        path = self._raw_path("qilt", "SAL_UG_ALL_2Y_AREA_E315.csv")
        if not path.exists():
            path = self._raw_path("qilt", "SAL_UG_ALL_2Y_DG_E315.csv")
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    def _load_eurostat(self) -> pd.DataFrame:
        full_csv = self.raw_dir / "eurostat" / "eurostat_employment_full.csv"
        if full_csv.exists():
            return pd.read_csv(full_csv)
        eurostat_dir = self.raw_dir / "eurostat"
        records: list[dict[str, object]] = []
        for path in sorted(eurostat_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            time_labels = payload["dimension"]["time"]["category"]["label"]
            geo_labels = payload["dimension"]["geo"]["category"]["label"]
            for geo_code, geo_name in geo_labels.items():
                values = payload.get("value", {})
                for idx, year in enumerate(time_labels.keys()):
                    value = values.get(str(idx))
                    if value is None:
                        continue
                    records.append(
                        {
                            "country": geo_name,
                            "geo_code": geo_code,
                            "year": int(year),
                            "employment_rate": float(value) / 100.0,
                            "dataset": payload.get("extension", {}).get("id", "EDAT_LFSE_24"),
                        }
                    )
        return pd.DataFrame(records)

    def _load_bls_employment(self) -> pd.DataFrame:
        path = self.raw_dir / "bls" / "bls_us_employment_proxy.csv"
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    def _load_eurostat_salary(self) -> pd.DataFrame:
        path = self.raw_dir / "eurostat_salary" / "germany_salary_bands.csv"
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    def _load_oflc(self) -> pd.DataFrame:
        oflc_dir = self.raw_dir / "oflc"
        xlsx_files = sorted(oflc_dir.glob("*.xlsx"))
        if not xlsx_files:
            return pd.DataFrame()
        for path in xlsx_files:
            try:
                frame = pd.read_excel(
                    path,
                    engine="openpyxl",
                    usecols=[
                        "SOC_CODE",
                        "SOC_TITLE",
                        "WAGE_RATE_OF_PAY_FROM",
                        "WAGE_RATE_OF_PAY_TO",
                        "WAGE_UNIT_OF_PAY",
                    ],
                )
                if not frame.empty:
                    return frame
            except Exception:
                continue
        return pd.DataFrame()

    def _load_nirf(self) -> pd.DataFrame:
        aggregated_path = self.raw_dir / "nirf" / "nirf_aggregated.csv"
        if aggregated_path.exists():
            frame = pd.read_csv(aggregated_path)
            if frame.empty:
                return frame
            return frame.assign(
                country="India",
                program_family="engineering",
                salary_median_lpa=lambda df: df["median_salary_inr"] / 100000.0,
                employment_rate=lambda df: df["placement_rate"],
                source_file="nirf_aggregated.csv",
            )[
                [
                    "country",
                    "program_family",
                    "institution_tier",
                    "salary_median_lpa",
                    "employment_rate",
                    "source_file",
                    "year",
                    "n_institutions",
                ]
            ]
        if pdfplumber is None:
            return pd.DataFrame()

        nirf_dir = self.raw_dir / "nirf"
        records: list[dict[str, object]] = []
        tier_map = {
            "IIIT_Hyderabad_IR-E-U-0014.pdf": 1,
            "IIT_Roorkee_IR-E-U-0560.pdf": 1,
            "University_of_Hyderabad_IR-E-U-0042.pdf": 2,
        }

        for path in sorted(nirf_dir.glob("*.pdf")):
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables() or []
                    for table in tables:
                        if not table:
                            continue
                        header = " ".join(str(cell or "") for cell in table[0]).lower()
                        if "median salary" not in header or "placed" not in header:
                            continue
                        for row in table[1:]:
                            cells = [str(cell or "").replace("\n", " ").strip() for cell in row]
                            if len(cells) < 8:
                                continue
                            graduating = self._safe_int(cells[4])
                            placed = self._safe_int(cells[5])
                            salary_rupees = self._extract_first_large_number(cells[6])
                            if graduating is None or placed is None or salary_rupees is None:
                                continue
                            if graduating <= 0 or placed < 0:
                                continue
                            records.append(
                                {
                                    "institution_name": path.stem,
                                    "country": "India",
                                    "program_family": "engineering",
                                    "institution_tier": tier_map.get(path.name, 3),
                                    "salary_median_lpa": salary_rupees / 100000.0,
                                    "employment_rate": min(1.0, placed / graduating),
                                    "source_file": path.name,
                                }
                            )
        return pd.DataFrame(records)

    def _load_statscan_placement(self) -> pd.DataFrame:
        statscan_dir = self.raw_dir / "statscan"
        ngs_path = statscan_dir / "canada_placement_ngs.csv"
        oecd_path = statscan_dir / "canada_placement_oecd_eag.csv"
        chosen = ngs_path if ngs_path.exists() else oecd_path
        return pd.read_csv(chosen) if chosen.exists() else pd.DataFrame()

    def _load_statscan_salary(self) -> pd.DataFrame:
        path = self.raw_dir / "statscan" / "canada_salary_ngs.csv"
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    def _safe_int(self, value: str) -> int | None:
        cleaned = value.replace(",", "").strip()
        return int(cleaned) if cleaned.isdigit() else None

    def _extract_first_large_number(self, value: str) -> int | None:
        matches = [int(match.replace(",", "")) for match in re.findall(r"(\d[\d,]{4,})", value)]
        if not matches:
            return None
        return matches[0]

    def _load_world_bank(self) -> pd.DataFrame:
        zip_path = self.raw_dir / "world_bank" / "world_bank_unemployment.zip"
        if not zip_path.exists():
            return pd.DataFrame()

        with zipfile.ZipFile(zip_path) as archive:
            target_name = next(
                (name for name in archive.namelist() if name.startswith("API_") and name.endswith(".csv")),
                None,
            )
            if target_name is None:
                return pd.DataFrame()

            with archive.open(target_name) as handle:
                frame = pd.read_csv(handle, skiprows=4)

        year_columns = [column for column in frame.columns if str(column).isdigit()]
        if not year_columns:
            return pd.DataFrame()

        melted = frame.melt(
            id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
            value_vars=year_columns,
            var_name="year",
            value_name="unemployment_rate",
        )
        melted["year"] = melted["year"].astype(int)
        melted["unemployment_rate"] = pd.to_numeric(melted["unemployment_rate"], errors="coerce")
        return melted.rename(
            columns={
                "Country Name": "country",
                "Country Code": "country_code",
                "Indicator Name": "indicator_name",
                "Indicator Code": "indicator_code",
            }
        ).dropna(subset=["unemployment_rate"])
