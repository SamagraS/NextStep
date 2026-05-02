import pytest

from app.schemas.common import BehavioralEngagement
from app.schemas.health import SSEStudentProfileUpdatedEvent
from app.services.demo_store import DemoStore
from app.services.notifier import DemoNotifier


class _DisconnectedRequest:
    async def is_disconnected(self) -> bool:
        return True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_notifier_stream_emits_initial_event():
    store = DemoStore()
    notifier = DemoNotifier(store)
    event = SSEStudentProfileUpdatedEvent(
        new_score=82,
        prev_score=74,
        delta=8,
        tenacity_score=0.9,
        behavioral_engagement=BehavioralEngagement.HIGH,
    )

    notifier.publish("application-1", event)

    chunks = []
    async for chunk in notifier.stream(_DisconnectedRequest(), "application-1"):
        chunks.append(chunk)
        if len(chunks) == 2:
            break

    assert chunks[0] == "event: student_profile_updated\n"
    assert chunks[1].startswith("data: ")
    assert "new_score" in chunks[1]