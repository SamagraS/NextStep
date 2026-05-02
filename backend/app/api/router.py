from fastapi import APIRouter

from app.api.routes import auth, outcomes, portfolio, score, student

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(score.router, prefix="/score", tags=["score"])
api_router.include_router(student.router, prefix="/student", tags=["student"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(outcomes.router, prefix="/outcomes", tags=["outcomes"])
