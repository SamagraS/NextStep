from dataclasses import dataclass

from app.schemas.score import (
    DelayedPlacementRisk,
    NextBestAction,
    PlacementProbability,
    RepaymentScore,
    SalaryForecast,
)


@dataclass(frozen=True)
class Layer1PlacementResult:
    placement_probability: PlacementProbability
    delayed_placement_risk: DelayedPlacementRisk
    employability_base_sub: float
    employability_final_sub: float
    base_rate: float
    strength_multiplier: float
    macro_adjustment: float
    tenacity_boost: float | None


@dataclass(frozen=True)
class Layer2SalaryResult:
    salary_forecast: SalaryForecast
    affordability_sub: float


@dataclass(frozen=True)
class Layer3RepaymentResult:
    repayment_score: RepaymentScore
    weakest_subscore: str


@dataclass(frozen=True)
class Layer4RecommendationResult:
    next_best_actions: list[NextBestAction]
