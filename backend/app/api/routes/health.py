from fastapi import APIRouter, Request

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    database_ok = await request.app.state.database.ping()
    artifact_snapshot = request.app.state.artifacts.snapshot()

    return HealthResponse(
        status="ok" if database_ok else "degraded",
        service=request.app.state.settings.app_name,
        version=request.app.state.settings.app_version,
        database={
            "status": "ok" if database_ok else "error",
            "driver": "sqlite+aiosqlite",
        },
        artifacts=artifact_snapshot,
    )
