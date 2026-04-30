from fastapi import APIRouter

from app.api.routes import outcomes, portfolio, score, student

api_router = APIRouter()
api_router.include_router(score.router, prefix="/score", tags=["score"])
api_router.include_router(student.router, prefix="/student", tags=["student"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(outcomes.router, prefix="/outcomes", tags=["outcomes"])
