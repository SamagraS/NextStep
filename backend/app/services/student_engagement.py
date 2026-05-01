from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.schemas.health import SSEStudentProfileUpdatedEvent
from app.schemas.student import StudentActionCompleteRequest
from app.services.demo_store import DemoStore
from app.services.notifier import DemoNotifier
from app.services.scoring import DemoScoringService

if TYPE_CHECKING:
    from app.services.persistence import PersistenceService


@dataclass(frozen=True)
class ActionCompletionOutcome:
    student_found: bool
    action_found: bool
    changed: bool


class StudentEngagementService:
    def __init__(
        self,
        store: DemoStore,
        notifier: DemoNotifier,
        artifacts=None,
        persistence: "PersistenceService | None" = None,
    ) -> None:
        self.store = store
        self.notifier = notifier
        self.artifacts = artifacts
        self.persistence = persistence

    async def complete_action(self, payload: StudentActionCompleteRequest) -> ActionCompletionOutcome:
        result = self.store.mark_dashboard_action_completed(payload.student_id, payload.action_id)
        if not result.student_found:
            return ActionCompletionOutcome(student_found=False, action_found=False, changed=False)
        if not result.action_found:
            return ActionCompletionOutcome(student_found=True, action_found=False, changed=False)
        if not result.changed:
            return ActionCompletionOutcome(student_found=True, action_found=True, changed=False)

        scoring_service = DemoScoringService(self.store, artifacts=self.artifacts)
        action = result.action

        for application_id in self.store.get_application_ids_for_student(payload.student_id):
            previous = self.store.get_application(application_id)
            previous_score = previous.response.repayment_score.score if previous else 71
            updated = scoring_service.rebuild_application(application_id)
            if updated is None:
                continue

            event = SSEStudentProfileUpdatedEvent(
                new_score=updated.repayment_score.score,
                prev_score=previous_score,
                delta=updated.repayment_score.score - previous_score,
                tenacity_score=updated.reliability.tenacity_score,
                behavioral_engagement=updated.reliability.behavioral_engagement,
            )
            self.notifier.publish(application_id, event)

            # DB persistence — best-effort, never blocks demo
            if self.persistence and action is not None:
                try:
                    await self.persistence.upsert_student_action(
                        action_id=action.action_id,
                        student_id=payload.student_id,
                        action_type=action.action_type,
                        title=action.title,
                        status="completed",
                        assigned_at=action.assigned_at,
                        expected_effort_hours=action.expected_effort_hours,
                        total_active_seconds=action.total_active_seconds,
                        return_visits=action.return_visits,
                        certificate_uploaded=action.certificate_uploaded,
                        completed_at=action.completed_at,
                        bandit_arm_index=payload.bandit_arm_index,
                        score_before=float(previous_score),
                        score_after=float(updated.repayment_score.score),
                        reward_signal=float(updated.repayment_score.score - previous_score),
                    )
                    await self.persistence.update_scoring_result_after_action(
                        application_id=application_id,
                        new_score=updated.repayment_score.score,
                        new_tier=updated.repayment_score.tier.value,
                        new_tenacity_score=updated.reliability.tenacity_score,
                        new_behavioral_engagement=updated.reliability.behavioral_engagement.value,
                        response_json=updated.model_dump_json(),
                    )
                except Exception:
                    pass  # DB write failure never blocks demo

        return ActionCompletionOutcome(student_found=True, action_found=True, changed=True)

