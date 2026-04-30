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


class PortfolioRescoreSummary(StrictSchema):
    total_active_cohorts: int = Field(ge=0)
    amber_count: int = Field(ge=0)
    red_count: int = Field(ge=0)
    latest_alerts: list[CohortAlert]
