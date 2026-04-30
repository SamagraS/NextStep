from app.outcomes.inference import OutcomeInferenceEngine
from app.schemas.outcomes import OutcomePredictionRequest, OutcomePredictionResponse


class OutcomeForecastService:
    def __init__(self, settings) -> None:
        self.engine = OutcomeInferenceEngine(
            data_dir=settings.data_dir,
            processed_dir=settings.processed_data_dir,
            mappings_dir=settings.mappings_dir,
        )

    def predict(self, payload: OutcomePredictionRequest) -> OutcomePredictionResponse:
        return self.engine.predict(payload)
