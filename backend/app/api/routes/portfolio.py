from fastapi import APIRouter, Request, Response, status

from app.services.portfolio_monitor import PortfolioMonitorService

router = APIRouter()


@router.post("/rescore", status_code=status.HTTP_202_ACCEPTED)
async def trigger_portfolio_rescore(request: Request) -> Response:
    PortfolioMonitorService(request.app.state.demo_store).trigger_demo_rescore()
    return Response(status_code=status.HTTP_202_ACCEPTED)
