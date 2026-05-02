from fastapi import APIRouter, Request, Response, status

from app.schemas.portfolio import CohortAlert, CohortRow, PortfolioDashboardResponse
from app.services.persistence import PersistenceService
from app.services.portfolio_monitor import PortfolioMonitorService

router = APIRouter()


@router.get("/dashboard", response_model=PortfolioDashboardResponse)
async def get_portfolio_dashboard(request: Request) -> PortfolioDashboardResponse:
    persistence = PersistenceService(request.app.state.database)
    service = PortfolioMonitorService(request.app.state.demo_store, persistence=persistence)
    stats = service.get_stats()
    return PortfolioDashboardResponse(
        total_active_cohorts=stats["total_active_cohorts"],
        amber_count=stats["amber_count"],
        red_count=stats["red_count"],
        cohorts=service.get_cohorts(),
        latest_alerts=service.get_alerts(),
    )


@router.get("/cohorts", response_model=list[CohortRow])
async def get_portfolio_cohorts(request: Request) -> list[CohortRow]:
    persistence = PersistenceService(request.app.state.database)
    return PortfolioMonitorService(request.app.state.demo_store, persistence=persistence).get_cohorts()


@router.get("/alerts", response_model=list[CohortAlert])
async def get_portfolio_alerts(request: Request) -> list[CohortAlert]:
    persistence = PersistenceService(request.app.state.database)
    return PortfolioMonitorService(request.app.state.demo_store, persistence=persistence).get_alerts()


@router.post("/rescore", status_code=status.HTTP_202_ACCEPTED)
async def trigger_portfolio_rescore(request: Request) -> Response:
    persistence = PersistenceService(request.app.state.database)
    await PortfolioMonitorService(request.app.state.demo_store, persistence=persistence).trigger_demo_rescore()
    return Response(status_code=status.HTTP_202_ACCEPTED)
