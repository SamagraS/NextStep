from pydantic import Field

from app.schemas.common import BehavioralEngagement, StrictSchema
from app.schemas.score import EmployerMatch


class ActionPlanItem(StrictSchema):
    action_id: str
    action_type: str
    title: str
    rationale: str
    assigned_at: str
    expected_effort_hours: float = Field(ge=0)
    total_active_seconds: int = Field(ge=0)
    return_visits: int = Field(ge=0)
    certificate_uploaded: bool
    completed_at: str | None = None


class TenacitySummary(StrictSchema):
    tenacity_score: float | None = Field(default=None, ge=0, le=1)
    behavioral_engagement: BehavioralEngagement
    data_points: int = Field(ge=0)
    summary: str


class MacroSummary(StrictSchema):
    destination_country: str
    summary: str
    macro_snapshot_ts: str


class StudentDashboardResponse(StrictSchema):
    full_name: str
    readiness_score: float = Field(ge=0, le=100)
    action_plan: list[ActionPlanItem]
    completed_actions: list[ActionPlanItem]
    pending_actions: list[ActionPlanItem]
    tenacity_summary: TenacitySummary
    macro_summary: MacroSummary
    employer_matches: list[EmployerMatch]


class StudentActionCompleteRequest(StrictSchema):
    student_id: str
    action_id: str
    bandit_arm_index: int = Field(ge=0, le=4)
