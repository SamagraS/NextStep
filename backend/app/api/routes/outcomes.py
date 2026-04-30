from fastapi import APIRouter, Request

from app.schemas.outcomes import OutcomePredictionRequest, OutcomePredictionResponse
from app.services.outcomes import OutcomeForecastService

router = APIRouter()


@router.post("/predict", response_model=OutcomePredictionResponse)
async def predict_outcome(
    request: Request,
    payload: OutcomePredictionRequest,
) -> OutcomePredictionResponse:
    service = OutcomeForecastService(settings=request.app.state.settings)
    return service.predict(payload)
