from pathlib import Path

from pydantic import Field

from app.schemas.common import BehavioralEngagement, StrictSchema


class ArtifactHealth(StrictSchema):
    name: str
    expected_path: Path
    loaded: bool
    source: str
    detail: str | None = None


class DatabaseHealth(StrictSchema):
    status: str
    driver: str


class HealthResponse(StrictSchema):
    status: str
    service: str
    version: str
    database: DatabaseHealth
    artifacts: list[ArtifactHealth]


class SSEStudentProfileUpdatedEvent(StrictSchema):
    new_score: int
    prev_score: int
    delta: int
    tenacity_score: float | None = None
    behavioral_engagement: BehavioralEngagement


class SSEHeartbeatEvent(StrictSchema):
    ts: str = Field(description="UTC ISO-8601 timestamp")
