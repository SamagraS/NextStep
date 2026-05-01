from typing import Any

from app.models.feature_assembly import FeatureAssemblyResult
from app.models.scoring_pipeline import Layer1PlacementResult
from app.schemas.common import DelayedPlacementFlag, MoratoriumWindow
from app.schemas.score import DelayedPlacementRisk, PlacementProbability


class Layer1PlacementService:
    def __init__(self, artifacts: Any | None = None) -> None:
        self.artifacts = artifacts

    def score(self, assembled: FeatureAssemblyResult) -> Layer1PlacementResult:
        p_without_behavioral = self._placement_probability(assembled, tenacity_score=None)
        p_with_behavioral = self._placement_probability(
            assembled,
            tenacity_score=assembled.tenacity.tenacity_score,
        )
        moratorium_months = int(assembled.feature_dict["moratorium_months"])
        employability_base = self._moratorium_relative_probability(
            moratorium_months=moratorium_months,
            placement=p_without_behavioral,
        )
        employability_final = self._moratorium_relative_probability(
            moratorium_months=moratorium_months,
            placement=p_with_behavioral,
        )
        delayed = self._delayed_placement_risk(
            p_3mo=p_with_behavioral.p_3mo,
            p_6mo=p_with_behavioral.p_6mo,
        )

        base_rate = self._base_rate_anchor(assembled, moratorium_months)
        macro_adjustment = round(0.9 + (assembled.macro.market_risk_sub * 0.1), 3)
        denominator = max(base_rate * macro_adjustment, 0.001)
        strength_multiplier = round(max(employability_base / denominator, 0.5), 3)
        tenacity_boost = (
            round(assembled.tenacity.tenacity_score * 0.10, 3)
            if assembled.tenacity.tenacity_score is not None
            else None
        )

        return Layer1PlacementResult(
            placement_probability=p_with_behavioral,
            delayed_placement_risk=delayed,
            employability_base_sub=employability_base,
            employability_final_sub=employability_final,
            base_rate=base_rate,
            strength_multiplier=strength_multiplier,
            macro_adjustment=macro_adjustment,
            tenacity_boost=tenacity_boost,
        )

    def _placement_probability(
        self,
        assembled: FeatureAssemblyResult,
        tenacity_score: float | None,
    ) -> PlacementProbability:
        cgpa_value = float(assembled.cgpa.resolved_value or 7.0)
        internship_value = int(assembled.internship_count.resolved_value or 0)
        cgpa_adj = (cgpa_value - 7.0) * 0.03
        internship_adj = min(internship_value, 3) * 0.03
        sector_adj = (
            0.03 if "cloud" in str(assembled.feature_dict["target_sector"]).lower() else 0.01
        )
        institution_adj = {1: 0.0, 2: -0.02, 3: -0.04}.get(
            int(assembled.feature_dict["institution_tier"]),
            -0.04,
        )
        program_family = str(assembled.feature_dict["program_family"])
        if program_family == "computer_science":
            program_adj = 0.0
        elif program_family == "data_science":
            program_adj = -0.01
        elif program_family == "business":
            program_adj = -0.02
        else:
            program_adj = -0.03

        behavior_adj = (tenacity_score or 0.0) * 0.04
        p_3mo = max(
            0.18,
            min(
                0.75,
                0.36
                + cgpa_adj
                + internship_adj
                + sector_adj
                + institution_adj
                + program_adj
                + behavior_adj,
            ),
        )
        p_6mo = max(p_3mo, min(0.92, p_3mo + 0.22))
        p_12mo = max(p_6mo, min(0.98, p_6mo + 0.13))

        return PlacementProbability(
            p_3mo=round(p_3mo, 3),
            p_6mo=round(p_6mo, 3),
            p_12mo=round(p_12mo, 3),
            monotonic_corrected=False,
            moratorium_window_used=self._moratorium_window(
                int(assembled.feature_dict["moratorium_months"])
            ),
            moratorium_months=int(assembled.feature_dict["moratorium_months"]),
        )

    def _moratorium_window(self, moratorium_months: int) -> MoratoriumWindow:
        if moratorium_months <= 3:
            return MoratoriumWindow.three_months
        if moratorium_months <= 6:
            return MoratoriumWindow.six_months
        return MoratoriumWindow.twelve_months

    def _moratorium_relative_probability(
        self,
        moratorium_months: int,
        placement: PlacementProbability,
    ) -> float:
        window = self._moratorium_window(moratorium_months)
        if window == MoratoriumWindow.three_months:
            return placement.p_3mo
        if window == MoratoriumWindow.six_months:
            return placement.p_6mo
        return placement.p_12mo

    def _delayed_placement_risk(self, p_3mo: float, p_6mo: float) -> DelayedPlacementRisk:
        gap = round(p_6mo - p_3mo, 3)
        if gap >= 0.3:
            flag = DelayedPlacementFlag.HIGH
            reason = "Most placement momentum appears after the early post-graduation window."
        elif gap >= 0.18:
            flag = DelayedPlacementFlag.MODERATE
            reason = (
                "Placement is more likely after the moratorium window than within the first 3 months."
            )
        else:
            flag = DelayedPlacementFlag.LOW
            reason = "Early and medium-horizon placement probabilities are closely aligned."
        return DelayedPlacementRisk(flag=flag, reason=reason, p3_p6_gap=gap)

    def _base_rate_anchor(
        self,
        assembled: FeatureAssemblyResult,
        moratorium_months: int,
    ) -> float:
        aggregate_outcomes = self.artifacts.get("aggregate_outcomes") if self.artifacts else None
        destination = str(assembled.macro.destination_country).lower()
        program_family = str(assembled.feature_dict["program_family"])

        window = self._moratorium_window(moratorium_months).value
        if isinstance(aggregate_outcomes, dict):
            key = (destination, program_family, window)
            value = aggregate_outcomes.get(key)
            if isinstance(value, (int, float)):
                return round(float(value), 3)

        default_base_rates = {
            ("united states", "computer_science", "12mo"): 0.56,
            ("united states", "computer_science", "6mo"): 0.48,
            ("united states", "computer_science", "3mo"): 0.34,
            ("united states", "data_science", "12mo"): 0.53,
            ("united states", "business", "12mo"): 0.49,
        }
        return round(default_base_rates.get((destination, program_family, window), 0.5), 3)
