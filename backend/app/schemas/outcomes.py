from pydantic import ConfigDict, Field

from app.schemas.common import StrictSchema


class OutcomePredictionRequest(StrictSchema):
    model_config = ConfigDict(extra="forbid", strict=True)

    program_family: str = Field(min_length=2, max_length=100)
    destination_country: str = Field(min_length=2, max_length=100)
    institution_tier: int = Field(ge=1, le=3)


class PlacementProbabilities(StrictSchema):
    p_3_months: float = Field(ge=0, le=1)
    p_6_months: float = Field(ge=0, le=1)
    p_12_months: float = Field(ge=0, le=1)
    macro_factor: float = Field(gt=0)


class SalaryBand(StrictSchema):
    currency: str
    p15: float = Field(ge=0)
    p50: float = Field(ge=0)
    p85: float = Field(ge=0)
    method: str


class RiskScore(StrictSchema):
    value: float = Field(ge=0, le=100)
    unemployment_rate: float | None = Field(default=None, ge=0, le=100)
    placement_stability: float = Field(ge=0, le=1)
    label: str


class OutcomePredictionResponse(StrictSchema):
    student_context: dict[str, str | int]
    placement_probabilities: PlacementProbabilities
    salary_band: SalaryBand
    risk_score: RiskScore
    sources_used: list[str]
    notes: list[str]

