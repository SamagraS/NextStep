from pydantic import Field

from app.schemas.common import StrictSchema


class CohortAlert(StrictSchema):
    cohort_id: str
    severity: str
    delta: float
    primary_macro_driver: str
    recommended_action: str
    macro_snapshot_ts: str
    triggered_at: str


class CohortRow(StrictSchema):
    cohort_id: str
    program_name: str
    destination_country: str
    cohort_size: int
    baseline_score: float
    current_score: float
    delta: float
    severity: str | None = None
    triggered_at: str | None = None
    primary_macro_driver: str | None = None


class PortfolioRescoreSummary(StrictSchema):
    total_active_cohorts: int = Field(ge=0)
    amber_count: int = Field(ge=0)
    red_count: int = Field(ge=0)
    latest_alerts: list[CohortAlert]


class PortfolioDashboardResponse(StrictSchema):
    total_active_cohorts: int = Field(ge=0)
    amber_count: int = Field(ge=0)
    red_count: int = Field(ge=0)
    cohorts: list[CohortRow]
    latest_alerts: list[CohortAlert]
