from app.models.scoring_pipeline import Layer1PlacementResult, Layer2SalaryResult, Layer3RepaymentResult
from app.schemas.common import Tier
from app.schemas.score import RepaymentScore


class Layer3RepaymentService:
    BASE_SCORE_CALIBRATION = 0.907

    def score(
        self,
        placement: Layer1PlacementResult,
        salary: Layer2SalaryResult,
        market_risk_sub: float,
        data_confidence_sub: float,
        moratorium_months: int,
        tenacity_score: float | None,
        completion_bonus_points: int,
    ) -> Layer3RepaymentResult:
        weighted_base_score = int(
            round(
                (
                    0.35 * placement.employability_base_sub
                    + 0.30 * salary.affordability_sub
                    + 0.20 * market_risk_sub
                    + 0.15 * data_confidence_sub
                )
                * 100
            )
        )
        base_score_without_behavioral = max(
            0,
            min(int(round(weighted_base_score * self.BASE_SCORE_CALIBRATION)), 100),
        )

        behavioral_boost_points = None
        if tenacity_score is not None:
            behavioral_boost_points = (
                min(int(round(tenacity_score * 4)), 3) + completion_bonus_points
            )

        final_score = max(
            0,
            min(base_score_without_behavioral + (behavioral_boost_points or 0), 100),
        )

        weakest_subscore = min(
            {
                "employability": placement.employability_final_sub,
                "affordability": salary.affordability_sub,
                "market_risk": market_risk_sub,
                "data_confidence": data_confidence_sub,
            },
            key=lambda item: {
                "employability": placement.employability_final_sub,
                "affordability": salary.affordability_sub,
                "market_risk": market_risk_sub,
                "data_confidence": data_confidence_sub,
            }[item],
        )

        return Layer3RepaymentResult(
            repayment_score=RepaymentScore(
                score=final_score,
                tier=self._tier(final_score),
                base_score_without_behavioral=(
                    base_score_without_behavioral if tenacity_score is not None else None
                ),
                behavioral_boost_points=behavioral_boost_points,
                employability_sub=placement.employability_final_sub,
                affordability_sub=salary.affordability_sub,
                market_risk_sub=market_risk_sub,
                data_confidence_sub=data_confidence_sub,
                moratorium_months_used=moratorium_months,
            ),
            weakest_subscore=weakest_subscore,
        )

    def _tier(self, score: int) -> Tier:
        if score >= 65:
            return Tier.GREEN
        if score >= 40:
            return Tier.AMBER
        return Tier.RED
