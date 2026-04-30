from typing import Literal
from uuid import uuid4

from pydantic import ConfigDict, Field, model_validator

from app.schemas.common import (
    BehavioralEngagement,
    DataCoverageLevel,
    DelayedPlacementFlag,
    MoratoriumWindow,
    RecommendationConfidence,
    ReliabilityBand,
    StrictSchema,
    Tier,
    UniversityMatchStatus,
)


class OriginationScoringRequest(StrictSchema):
    model_config = ConfigDict(extra="forbid", strict=True)

    student_id: str | None = None
    full_name: str = Field(min_length=1, max_length=200)
    university_name: str = Field(min_length=1, max_length=255)
    program_name: str = Field(min_length=1, max_length=255)
    destination_country: str = Field(min_length=2, max_length=100)
    target_sector: str = Field(min_length=1, max_length=100)
    cgpa: float | None = Field(default=None, ge=0, le=10)
    cgpa_present: bool = False
    internship_count: int | None = Field(default=None, ge=0, le=20)
    internship_count_present: bool = False
    stem_opt_eligible: bool | None = None
    stem_opt_eligible_present: bool = False
    loan_amount_inr: float = Field(gt=0)
    interest_rate_annual_pct: float = Field(gt=0, le=100)
    repayment_term_months: int = Field(gt=0, le=600)
    moratorium_months: int = Field(ge=0, le=120)

    @model_validator(mode="after")
    def validate_present_flags(self) -> "OriginationScoringRequest":
        present_pairs = (
            ("cgpa", "cgpa_present"),
            ("internship_count", "internship_count_present"),
            ("stem_opt_eligible", "stem_opt_eligible_present"),
        )
        for value_field, present_field in present_pairs:
            value = getattr(self, value_field)
            is_present = getattr(self, present_field)
            if is_present and value is None:
                raise ValueError(f"{value_field} must be provided when {present_field} is true.")
            if not is_present and value is not None:
                raise ValueError(f"{value_field} must be null when {present_field} is false.")
        return self


class PlacementProbability(StrictSchema):
    p_3mo: float = Field(ge=0, le=1)
    p_6mo: float = Field(ge=0, le=1)
    p_12mo: float = Field(ge=0, le=1)
    monotonic_corrected: bool
    moratorium_window_used: MoratoriumWindow
    moratorium_months: int = Field(ge=0)


class DelayedPlacementRisk(StrictSchema):
    flag: DelayedPlacementFlag
    reason: str
    p3_p6_gap: float


class SalaryProgressionScenario(StrictSchema):
    year_1: float
    year_2: float
    year_3: float
    basis: str


class SalaryForecast(StrictSchema):
    method: Literal["xgboost_quantile_regression_us", "percentile_band_lookup"]
    source_note: str
    currency: Literal["USD_nominal"]
    pessimistic: float
    realistic: float
    optimistic: float
    salary_progression_scenario: SalaryProgressionScenario
    emi_monthly_usd: float
    emi_as_pct_realistic: float


class RepaymentScore(StrictSchema):
    score: int = Field(ge=0, le=100)
    tier: Tier
    base_score_without_behavioral: int | None = Field(default=None, ge=0, le=100)
    behavioral_boost_points: int | None = Field(default=None)
    employability_sub: float = Field(ge=0, le=1)
    affordability_sub: float = Field(ge=0, le=1)
    market_risk_sub: float = Field(ge=0, le=1)
    data_confidence_sub: float = Field(ge=0, le=1)
    moratorium_months_used: int = Field(ge=0)


class TenacityBreakdown(StrictSchema):
    avg_completion_rate: float = Field(ge=0, le=1)
    avg_engagement_depth: float = Field(ge=0, le=1)
    avg_consistency: float = Field(ge=0, le=1)
    certifications_verified: int = Field(ge=0)


class Reliability(StrictSchema):
    band: ReliabilityBand
    behavioral_engagement: BehavioralEngagement
    tenacity_score: float | None = Field(default=None, ge=0, le=1)
    tenacity_data_count: int = Field(ge=0)
    tenacity_breakdown: TenacityBreakdown | None = None
    imputation_flags: list[str]
    university_match: UniversityMatchStatus
    university_match_score: int = Field(ge=0, le=100)
    data_coverage_level: DataCoverageLevel
    macro_snapshot_ts: str
    stale_signal_warning: str | None = None


class NextBestAction(StrictSchema):
    rank: int = Field(ge=1)
    action_type: str
    rationale: str
    recommendation_confidence: RecommendationConfidence
    ucb_raw: float
    bandit_version: str


class EmployerMatch(StrictSchema):
    employer: str
    median_salary_usd: float
    annual_h1b_filings: int = Field(ge=0)
    visa_approval_rate: float = Field(ge=0, le=1)


class ExplanationAttribution(StrictSchema):
    base_rate: float
    strength_multiplier: float
    macro_adjustment: float
    tenacity_boost: float | None = None


class Explanation(StrictSchema):
    tier_1: str
    tier_2_positive: list[str]
    tier_2_risk: list[str]
    tier_2_attribution: ExplanationAttribution


class ModelMetadata(StrictSchema):
    model_version: str
    macro_snapshot_ts: str
    training_data_cutoff: str
    l1_method: str
    l2_method: str
    l3_method: str
    l4_method: str


class ScoringResponse(StrictSchema):
    application_id: str = Field(default_factory=lambda: str(uuid4()))
    placement_probability: PlacementProbability
    delayed_placement_risk: DelayedPlacementRisk
    salary_forecast: SalaryForecast
    repayment_score: RepaymentScore
    reliability: Reliability
    next_best_action: list[NextBestAction]
    employer_match_list: list[EmployerMatch]
    explanation: Explanation
    model_metadata: ModelMetadata


class ScoreLatestResponse(StrictSchema):
    score: int = Field(ge=0, le=100)
    tier: Tier
    tenacity_score: float | None = Field(default=None, ge=0, le=1)
    behavioral_engagement: BehavioralEngagement
    scored_at: str
