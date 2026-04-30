from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app.outcomes.ingestion import DatasetIngestor
from app.outcomes.mapping import TaxonomyMapper
from app.outcomes.models.macro import MacroRiskModel
from app.outcomes.models.placement import PlacementModel
from app.outcomes.models.salary import SalaryModel
from app.outcomes.preprocessing import DatasetPreprocessor
from app.schemas.outcomes import (
    OutcomePredictionRequest,
    OutcomePredictionResponse,
    PlacementProbabilities,
    RiskScore,
    SalaryBand,
)


class OutcomeInferenceEngine:
    def __init__(self, data_dir: Path, processed_dir: Path, mappings_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.processed_dir = Path(processed_dir)
        self.mappings_dir = Path(mappings_dir)
        self.mapper = TaxonomyMapper()

    def build_artifacts(self) -> None:
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.mappings_dir.mkdir(parents=True, exist_ok=True)

        raw = DatasetIngestor(self.data_dir).load()
        standardized = DatasetPreprocessor(self.mapper).standardize(raw)

        placement_lookup = PlacementModel().build_lookup(standardized.placement)
        salary_lookup = SalaryModel().build_lookup(standardized.salary, standardized.salary_microdata)
        macro_lookup = MacroRiskModel().build_lookup(standardized.macro)

        placement_lookup.to_csv(self.processed_dir / "placement_lookup.csv", index=False)
        salary_lookup.to_csv(self.processed_dir / "salary_lookup.csv", index=False)
        macro_lookup.to_csv(self.processed_dir / "macro_lookup.csv", index=False)

        source_manifest = {
            "placement_sources": sorted(standardized.placement["source"].dropna().unique().tolist())
            if not standardized.placement.empty
            else [],
            "salary_sources": sorted(standardized.salary["source"].dropna().unique().tolist())
            if not standardized.salary.empty
            else [],
            "salary_microdata_sources": ["OFLC H1B"] if not standardized.salary_microdata.empty else [],
            "macro_sources": ["World Bank"] if not standardized.macro.empty else [],
        }
        (self.processed_dir / "source_manifest.json").write_text(
            json.dumps(source_manifest, indent=2),
            encoding="utf-8",
        )

    def predict(self, payload: OutcomePredictionRequest) -> OutcomePredictionResponse:
        self._ensure_artifacts()

        program_family = self.mapper.normalize_program_family(payload.program_family)
        country = self.mapper.normalize_country(payload.destination_country)
        tier = payload.institution_tier

        placement_lookup = pd.read_csv(self.processed_dir / "placement_lookup.csv")
        salary_lookup = pd.read_csv(self.processed_dir / "salary_lookup.csv")
        macro_lookup = pd.read_csv(self.processed_dir / "macro_lookup.csv")
        source_manifest = json.loads((self.processed_dir / "source_manifest.json").read_text(encoding="utf-8"))

        placement_row, placement_notes = self._select_placement_row(
            placement_lookup, program_family, country, tier
        )
        salary_row, salary_notes = self._select_salary_row(
            salary_lookup, program_family, country, tier
        )
        macro_row = self._select_macro_row(macro_lookup, country)

        macro_factor = float(macro_row.get("macro_factor", 1.0))
        p3 = round(min(0.99, float(placement_row["p3"]) * macro_factor), 4)
        p6 = round(min(0.995, max(p3, float(placement_row["p6"]) * macro_factor)), 4)
        p12 = round(min(0.999, max(p6, float(placement_row["p12"]) * macro_factor)), 4)

        stability = max(0.0, min(1.0, 1.0 - ((p12 - p3) * 0.65)))
        risk_value = round(
            max(
                0.0,
                min(
                    100.0,
                    (1.0 - ((p3 + p6 + p12) / 3.0)) * 100 + (1 - macro_factor) * 35,
                ),
            ),
            2,
        )
        risk_label = "low" if risk_value < 35 else "medium" if risk_value < 65 else "high"

        return OutcomePredictionResponse(
            student_context={
                "program_family": program_family,
                "country": country,
                "institution_tier": tier,
            },
            placement_probabilities=PlacementProbabilities(
                p_3_months=p3,
                p_6_months=p6,
                p_12_months=p12,
                macro_factor=macro_factor,
            ),
            salary_band=SalaryBand(
                currency=str(salary_row["currency"]),
                p15=round(float(salary_row["p15"]), 2),
                p50=round(float(salary_row["p50"]), 2),
                p85=round(float(salary_row["p85"]), 2),
                method=str(salary_row["method"]),
            ),
            risk_score=RiskScore(
                value=risk_value,
                unemployment_rate=(
                    float(macro_row["unemployment_rate"])
                    if "unemployment_rate" in macro_row and pd.notna(macro_row["unemployment_rate"])
                    else None
                ),
                placement_stability=round(stability, 4),
                label=risk_label,
            ),
            sources_used=sorted(
                set(
                    source_manifest.get("placement_sources", [])
                    + source_manifest.get("salary_sources", [])
                    + source_manifest.get("salary_microdata_sources", [])
                    + source_manifest.get("macro_sources", [])
                )
            ),
            notes=placement_notes + salary_notes,
        )

    def _ensure_artifacts(self) -> None:
        required = [
            self.processed_dir / "placement_lookup.csv",
            self.processed_dir / "salary_lookup.csv",
            self.processed_dir / "macro_lookup.csv",
            self.processed_dir / "source_manifest.json",
        ]
        if not all(path.exists() for path in required):
            self.build_artifacts()

    def _select_placement_row(
        self,
        lookup: pd.DataFrame,
        program_family: str,
        country: str,
        tier: int,
    ) -> tuple[pd.Series, list[str]]:
        notes: list[str] = []
        exact = lookup[
            (lookup["program_family"] == program_family)
            & (lookup["country"] == country)
            & (lookup["institution_tier"] == tier)
        ]
        if not exact.empty:
            return exact.iloc[0], notes

        country_match = lookup[(lookup["country"] == country) & (lookup["institution_tier"] == tier)]
        if not country_match.empty:
            notes.append(
                "Placement used country+tier fallback because an exact program-family match was unavailable."
            )
            return country_match.sort_values("base_rate", ascending=False).iloc[0], notes

        country_only = lookup[lookup["country"] == country]
        if not country_only.empty:
            notes.append("Placement used country-level fallback because an exact tiered match was unavailable.")
            return country_only.sort_values("base_rate", ascending=False).iloc[0], notes

        notes.append("Placement used global fallback because no country-specific record was available.")
        return lookup.sort_values("base_rate", ascending=False).iloc[0], notes

    def _select_salary_row(
        self,
        lookup: pd.DataFrame,
        program_family: str,
        country: str,
        tier: int,
    ) -> tuple[pd.Series, list[str]]:
        notes: list[str] = []
        exact = lookup[
            (lookup["program_family"] == program_family)
            & (lookup["country"] == country)
            & (lookup["institution_tier"] == tier)
        ]
        if not exact.empty:
            return exact.iloc[0], notes

        country_program = lookup[(lookup["program_family"] == program_family) & (lookup["country"] == country)]
        if not country_program.empty:
            notes.append("Salary used country+program fallback because tier-specific data was unavailable.")
            return country_program.iloc[0], notes

        country_general = lookup[(lookup["program_family"] == "general_studies") & (lookup["country"] == country)]
        if not country_general.empty:
            notes.append("Salary used country-level aggregate fallback because program-specific data was unavailable.")
            return country_general.iloc[0], notes

        notes.append("Salary used global fallback because no country-specific record was available.")
        return lookup.iloc[0], notes

    def _select_macro_row(self, lookup: pd.DataFrame, country: str) -> pd.Series:
        match = lookup[lookup["country"] == country]
        if not match.empty:
            return match.iloc[0]
        return pd.Series({"country": country, "macro_factor": 1.0, "unemployment_rate": None})

