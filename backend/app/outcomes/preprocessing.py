from __future__ import annotations

import math
import re
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.outcomes.mapping import TaxonomyMapper

# Suppress numpy RuntimeWarnings from internal nanmean operations on edge cases
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy.lib._nanfunctions_impl")


@dataclass(frozen=True)
class StandardizedDatasetBundle:
    placement: pd.DataFrame
    salary: pd.DataFrame
    macro: pd.DataFrame
    salary_microdata: pd.DataFrame


class DatasetPreprocessor:
    def __init__(self, mapper: TaxonomyMapper) -> None:
        self.mapper = mapper

    def standardize(self, raw) -> StandardizedDatasetBundle:
        placement_frames = [
            self._standardize_hesa(raw.hesa_subject),
            self._standardize_qilt_employment(raw.qilt_employment),
            self._standardize_eurostat(raw.eurostat),
            self._standardize_bls(raw.bls_employment),
            self._standardize_nirf_placement(raw.nirf),
        ]
        salary_frames = [
            self._standardize_qilt_salary(raw.qilt_salary),
            self._standardize_hesa_salary(raw.hesa_salary),
            self._standardize_nirf_salary(raw.nirf),
        ]
        placement_parts = [
            frame.dropna(how="all", axis=0).dropna(how="all", axis=1)
            for frame in placement_frames
        ]
        placement_parts = [frame for frame in placement_parts if not frame.empty]
        salary_parts = [
            frame.dropna(how="all", axis=0).dropna(how="all", axis=1)
            for frame in salary_frames
        ]
        salary_parts = [frame for frame in salary_parts if not frame.empty]
        placement = pd.concat(placement_parts, ignore_index=True) if placement_parts else pd.DataFrame()
        salary = pd.concat(salary_parts, ignore_index=True) if salary_parts else pd.DataFrame()
        macro = self._standardize_world_bank(raw.world_bank)
        salary_microdata = self._standardize_oflc(raw.oflc)
        return StandardizedDatasetBundle(
            placement=placement.dropna(how="all"),
            salary=salary.dropna(how="all"),
            macro=macro.dropna(how="all"),
            salary_microdata=salary_microdata.dropna(how="all"),
        )

    def _to_number(self, value) -> float | None:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        cleaned = str(value).replace(",", "").replace("%", "").strip()
        if cleaned == "":
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _standardize_hesa(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        working = frame.copy()
        working["program_family"] = working["Subject area of degree"].astype(str).map(
            self.mapper.map_hesa_subject
        )
        employed = working["Full-time employment"].map(self._to_number).fillna(0)
        further_study = working["Employmentand further study"].map(self._to_number).fillna(0)
        unemployed = working["Unemployed"].map(self._to_number).fillna(0)
        known = working["Total with known outcomes"].map(self._to_number).replace(0, np.nan)
        working["employment_rate"] = (employed + further_study) / known
        working["sample_size"] = known
        return pd.DataFrame(
            {
                "source": "HESA",
                "country": "United Kingdom",
                "program_family": working["program_family"],
                "institution_tier": 2,
                "employment_rate": working["employment_rate"],
                "unemployment_rate_source": unemployed / known,
                "sample_size": working["sample_size"],
            }
        ).dropna(subset=["employment_rate"])

    def _standardize_qilt_employment(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        rows: list[dict[str, object]] = []
        for _, row in frame.iterrows():
            label = str(row.iloc[1]) if len(row.index) > 1 else ""
            rate = self._to_number(row.iloc[-1])
            if not label or rate is None:
                continue
            rows.append(
                {
                    "source": "QILT",
                    "country": "Australia",
                    "program_family": self.mapper.map_qilt_field(label),
                    "institution_tier": 2,
                    "employment_rate": rate / 100.0,
                    "unemployment_rate_source": None,
                    "sample_size": 1.0,
                }
            )
        return pd.DataFrame(rows)

    def _standardize_eurostat(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        if {"program_family", "country", "employment_rate", "source"}.issubset(frame.columns):
            working = frame.copy()
            working["program_family"] = working["program_family"].map(self.mapper.normalize_program_family)
            return pd.DataFrame(
                {
                    "source": working["source"],
                    "country": working["country"].map(self.mapper.normalize_country),
                    "program_family": working["program_family"],
                    "institution_tier": 2,
                    "employment_rate": working["employment_rate"],
                    "unemployment_rate_source": None,
                    "sample_size": 1.0,
                }
            )
        latest = frame.sort_values("year").groupby("country", as_index=False).tail(1)
        return pd.DataFrame(
            {
                "source": "Eurostat",
                "country": latest["country"].map(self.mapper.normalize_country),
                "program_family": "general_studies",
                "institution_tier": 2,
                "employment_rate": latest["employment_rate"],
                "unemployment_rate_source": None,
                "sample_size": 1.0,
            }
        )

    def _standardize_bls(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        rows: list[dict[str, object]] = []
        for _, row in frame.iterrows():
            for tier in (1, 2, 3):
                rows.append(
                    {
                        "source": row.get("source", "BLS_OES_proxy"),
                        "country": "United States",
                        "program_family": self.mapper.normalize_program_family(str(row["program_family"])),
                        "institution_tier": tier,
                        "employment_rate": row["employment_rate"],
                        "unemployment_rate_source": None,
                        "sample_size": 1.0,
                    }
                )
        return pd.DataFrame(rows)

    def _standardize_nirf_placement(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        working = frame.dropna(subset=["employment_rate"]).copy()
        working["program_family"] = working["program_family"].map(self.mapper.normalize_program_family)
        return pd.DataFrame(
            {
                "source": "NIRF",
                "country": "India",
                "program_family": working["program_family"],
                "institution_tier": working["institution_tier"],
                "employment_rate": working["employment_rate"],
                "unemployment_rate_source": None,
                "sample_size": 1.0,
            }
        )

    def _standardize_qilt_salary(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        rows: list[dict[str, object]] = []
        for _, row in frame.iterrows():
            label = str(row.iloc[1]) if len(row.index) > 1 else ""
            value = self._to_number(row.iloc[-1])
            if not label or value is None:
                continue
            rows.append(
                {
                    "source": "QILT",
                    "country": "Australia",
                    "program_family": self.mapper.map_qilt_field(label),
                    "institution_tier": 2,
                    "salary_median": value,
                    "currency": "AUD",
                }
            )
        return pd.DataFrame(rows)

    def _standardize_hesa_salary(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()

        salary_bands: list[tuple[int, int, float]] = []
        for _, row in frame.iterrows():
            band = str(row.get("Salary band", ""))
            female = self._to_number(row.get("Female"))
            male = self._to_number(row.get("Male"))
            if "£" not in band and "Â£" not in band:
                continue
            shares = [value for value in (female, male) if value is not None and not np.isnan(value)]
            if not shares:
                continue
            average_share = float(np.mean(shares)) / 100.0
            numbers = [int(part.replace(",", "")) for part in re.findall(r"(\d[\d,]*)", band)]
            if len(numbers) == 1:
                low, high = numbers[0], numbers[0] + 5000
            else:
                low, high = numbers[0], numbers[1]
            salary_bands.append((low, high, average_share))

        if not salary_bands:
            return pd.DataFrame()

        cumulative = 0.0
        p15 = p50 = p85 = None
        for low, high, share in salary_bands:
            cumulative += share
            midpoint = (low + high) / 2
            if p15 is None and cumulative >= 0.15:
                p15 = midpoint
            if p50 is None and cumulative >= 0.50:
                p50 = midpoint
            if p85 is None and cumulative >= 0.85:
                p85 = midpoint

        return pd.DataFrame(
            [
                {
                    "source": "HESA",
                    "country": "United Kingdom",
                    "program_family": "general_studies",
                    "institution_tier": 2,
                    "salary_p15": p15,
                    "salary_median": p50,
                    "salary_p85": p85,
                    "currency": "GBP",
                }
            ]
        )

    def _standardize_nirf_salary(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        working = frame.dropna(subset=["salary_median_lpa"]).copy()
        return pd.DataFrame(
            {
                "source": "NIRF",
                "country": "India",
                "program_family": working["program_family"],
                "institution_tier": working["institution_tier"],
                "salary_median": working["salary_median_lpa"] * 100000.0,
                "currency": "INR",
            }
        )

    def _standardize_world_bank(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        filtered = frame[
            frame["country"].isin(
                ["United States", "United Kingdom", "Australia", "India", "Germany"]
            )
        ].copy()
        return filtered[["country", "year", "unemployment_rate"]]

    def _standardize_oflc(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()

        working = frame.copy()
        column_map = {column.lower(): column for column in working.columns}
        wage_from = column_map.get("wage_rate_of_pay_from")
        wage_to = column_map.get("wage_rate_of_pay_to")
        wage_unit = column_map.get("wage_unit_of_pay")
        soc_code = column_map.get("soc_code")
        soc_title = column_map.get("soc_title")
        if not all([wage_from, wage_to, wage_unit]):
            return pd.DataFrame()

        working["wage_from"] = pd.to_numeric(working[wage_from], errors="coerce")
        working["wage_to"] = pd.to_numeric(working[wage_to], errors="coerce")
        working["wage_unit"] = working[wage_unit].astype(str)
        working["soc_code_norm"] = working[soc_code].astype(str) if soc_code else ""
        working["soc_title_norm"] = working[soc_title].astype(str) if soc_title else ""
        working["program_family"] = working.apply(
            lambda row: self.mapper.map_soc_code(row["soc_code_norm"], row["soc_title_norm"]),
            axis=1,
        )
        working["annual_salary"] = working.apply(
            lambda row: self._annualize_wage(row["wage_from"], row["wage_to"], row["wage_unit"]),
            axis=1,
        )
        working = working[(working["annual_salary"] >= 15000) & (working["annual_salary"] <= 500000)]
        return working[["program_family", "annual_salary"]]

    def _annualize_wage(self, wage_from: float, wage_to: float, wage_unit: str) -> float:
        if pd.isna(wage_from):
            return np.nan
        amount = wage_from if pd.isna(wage_to) or wage_to <= 0 else (wage_from + wage_to) / 2.0
        unit = wage_unit.strip().upper()
        multipliers = {
            "YEAR": 1.0,
            "YR": 1.0,
            "MONTH": 12.0,
            "BI-WEEKLY": 26.0,
            "WEEK": 52.0,
            "HOUR": 2080.0,
        }
        multiplier = multipliers.get(unit)
        return amount * multiplier if multiplier else np.nan
