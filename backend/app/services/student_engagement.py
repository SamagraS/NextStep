from dataclasses import dataclass

from app.schemas.health import SSEStudentProfileUpdatedEvent
from app.schemas.student import StudentActionCompleteRequest
from app.services.demo_store import DemoStore
from app.services.notifier import DemoNotifier
from app.services.scoring import DemoScoringService


@dataclass(frozen=True)
class ActionCompletionOutcome:
    student_found: bool
    action_found: bool
    changed: bool


class StudentEngagementService:
    def __init__(self, store: DemoStore, notifier: DemoNotifier, artifacts=None) -> None:
        self.store = store
        self.notifier = notifier
        self.artifacts = artifacts

    async def complete_action(self, payload: StudentActionCompleteRequest) -> ActionCompletionOutcome:
        result = self.store.mark_dashboard_action_completed(payload.student_id, payload.action_id)
        if not result.student_found:
            return ActionCompletionOutcome(student_found=False, action_found=False, changed=False)
        if not result.action_found:
            return ActionCompletionOutcome(student_found=True, action_found=False, changed=False)
        if not result.changed:
            return ActionCompletionOutcome(student_found=True, action_found=True, changed=False)

        scoring_service = DemoScoringService(self.store, artifacts=self.artifacts)
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
        return ActionCompletionOutcome(student_found=True, action_found=True, changed=True)
