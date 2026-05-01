from fastapi import APIRouter, HTTPException, Request, Response, status

from app.schemas.student import (
    StudentActionCompleteRequest,
    StudentDashboardResponse,
)
from app.services.persistence import PersistenceService
from app.services.student_dashboard import StudentDashboardService
from app.services.student_engagement import StudentEngagementService

router = APIRouter()


@router.get("/dashboard/{student_id}", response_model=StudentDashboardResponse)
async def get_student_dashboard(request: Request, student_id: str) -> StudentDashboardResponse:
    service = StudentDashboardService(request.app.state.demo_store)
    dashboard = service.get_dashboard(student_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return dashboard


@router.post("/action/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_student_action(request: Request, payload: StudentActionCompleteRequest) -> Response:
    service = StudentEngagementService(
        store=request.app.state.demo_store,
        notifier=request.app.state.notifier,
        artifacts=request.app.state.artifacts,
        persistence=PersistenceService(request.app.state.database),
    )
    outcome = await service.complete_action(payload)
    if not outcome.student_found:
        raise HTTPException(status_code=404, detail="Student not found.")
    if not outcome.action_found:
        raise HTTPException(status_code=404, detail="Action not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
