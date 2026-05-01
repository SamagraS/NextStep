from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.schemas.score import (
    OriginationScoringRequest,
    ScoreLatestResponse,
    ScoringResponse,
)
from app.services.persistence import PersistenceService
from app.services.scoring import DemoScoringService

router = APIRouter()


@router.post("/origination", response_model=ScoringResponse)
async def score_origination(request: Request, payload: OriginationScoringRequest) -> ScoringResponse:
    service = DemoScoringService(
        store=request.app.state.demo_store,
        artifacts=request.app.state.artifacts,
    )
    response, scored_at = service.score_origination(payload)

    try:
        persistence = PersistenceService(request.app.state.database)
        await persistence.save_origination(
            application_id=response.application_id,
            student_id=payload.student_id,
            payload_json=payload.model_dump_json(),
            response_json=response.model_dump_json(),
            score=response.repayment_score.score,
            tier=response.repayment_score.tier.value,
            reliability_band=response.reliability.band.value,
            delayed_placement_risk=response.delayed_placement_risk.flag.value,
            behavioral_engagement=response.reliability.behavioral_engagement.value,
            tenacity_score=response.reliability.tenacity_score,
            macro_snapshot_ts=response.reliability.macro_snapshot_ts,
            scored_at=scored_at,
        )
    except Exception:
        pass  # DB failure never blocks demo

    return response


@router.get("/{application_id}/latest", response_model=ScoreLatestResponse)
async def get_latest_score(request: Request, application_id: str) -> ScoreLatestResponse:
    snapshot = request.app.state.demo_store.get_latest_score_snapshot(application_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Application not found.")

    score, tier, tenacity_score, behavioral_engagement, scored_at = snapshot
    return ScoreLatestResponse(
        score=score,
        tier=tier,
        tenacity_score=tenacity_score,
        behavioral_engagement=behavioral_engagement,
        scored_at=scored_at,
    )


@router.get(
    "/{application_id}/stream",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Server-Sent Events stream",
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                    "examples": {
                        "student_profile_updated": {
                            "summary": "Student profile update event",
                            "value": (
                                "event: student_profile_updated\n"
                                'data: {"new_score":74,"prev_score":71,"delta":3,'
                                '"tenacity_score":0.82,"behavioral_engagement":"HIGH"}\n\n'
                            ),
                        },
                        "heartbeat": {
                            "summary": "Heartbeat event",
                            "value": 'event: heartbeat\ndata: {"ts":"2026-04-14T10:00:00Z"}\n\n',
                        },
                    },
                }
            },
        }
    },
)
async def stream_score_updates(request: Request, application_id: str) -> StreamingResponse:
    return StreamingResponse(
        request.app.state.notifier.stream(request=request, application_id=application_id),
        media_type="text/event-stream",
    )
