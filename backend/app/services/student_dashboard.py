from app.schemas.student import (
    ActionPlanItem,
    MacroSummary,
    StudentDashboardResponse,
    TenacitySummary,
)
from app.services.demo_store import DemoStore, MOCK_SNAPSHOT_TS
from app.services.scoring import DemoScoringService


class StudentDashboardService:
    def __init__(self, store: DemoStore) -> None:
        self.store = store

    def get_dashboard(self, student_id: str) -> StudentDashboardResponse | None:
        student = self.store.get_student(student_id)
        if student is None:
            return None

        pending_actions = [
            self._to_action_plan_item(action)
            for action in self.store.get_dashboard_pending_actions(student_id)
        ]
        completed_actions = [
            self._to_action_plan_item(action)
            for action in self.store.get_dashboard_completed_actions(student_id)
        ]

        scoring = DemoScoringService(self.store)
        employer_matches = scoring._employer_matches(
            destination_country=student.destination_country,
            program_family=student.program_family,
        )

        return StudentDashboardResponse(
            readiness_score=self.store.get_readiness_score(student_id),
            action_plan=pending_actions + completed_actions,
            completed_actions=completed_actions,
            pending_actions=pending_actions,
            tenacity_summary=TenacitySummary(
                tenacity_score=self.store.get_tenacity_score(student_id),
                behavioral_engagement=self.store.get_behavioral_engagement(student_id),
                data_points=len(student.preloan_actions),
                summary="Strong pre-loan engagement across multiple actions and return visits.",
            ),
            macro_summary=MacroSummary(
                destination_country=student.destination_country,
                summary=student.macro_summary,
                macro_snapshot_ts=MOCK_SNAPSHOT_TS,
            ),
            employer_matches=employer_matches,
        )

    def _to_action_plan_item(self, action) -> ActionPlanItem:
        return ActionPlanItem(
            action_id=action.action_id,
            action_type=action.action_type,
            title=action.title,
            rationale=action.rationale,
            assigned_at=action.assigned_at,
            expected_effort_hours=action.expected_effort_hours,
            total_active_seconds=action.total_active_seconds,
            return_visits=action.return_visits,
            certificate_uploaded=action.certificate_uploaded,
            completed_at=action.completed_at,
        )
