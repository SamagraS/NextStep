import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator

from fastapi import Request

from app.schemas.health import SSEHeartbeatEvent, SSEStudentProfileUpdatedEvent
from app.services.demo_store import DemoStore, MOCK_SNAPSHOT_TS


class DemoNotifier:
    def __init__(self, store: DemoStore) -> None:
        self.store = store
        self._subscribers: dict[str, list[asyncio.Queue[SSEStudentProfileUpdatedEvent]]] = defaultdict(list)

    def publish(self, application_id: str, event: SSEStudentProfileUpdatedEvent) -> None:
        self.store.set_latest_event(application_id, event)
        for queue in list(self._subscribers.get(application_id, [])):
            queue.put_nowait(event)

    async def stream(self, request: Request, application_id: str) -> AsyncIterator[str]:
        queue: asyncio.Queue[SSEStudentProfileUpdatedEvent] = asyncio.Queue()
        self._subscribers[application_id].append(queue)

        initial_event = self.store.get_latest_event(application_id)
        if initial_event is not None:
            yield "event: student_profile_updated\n"
            yield f"data: {initial_event.model_dump_json()}\n\n"

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield "event: student_profile_updated\n"
                    yield f"data: {event.model_dump_json()}\n\n"
                except TimeoutError:
                    heartbeat = SSEHeartbeatEvent(ts=MOCK_SNAPSHOT_TS)
                    yield "event: heartbeat\n"
                    yield f"data: {heartbeat.model_dump_json()}\n\n"
        finally:
            self._subscribers[application_id] = [
                subscriber
                for subscriber in self._subscribers[application_id]
                if subscriber is not queue
            ]
