import json

from app.core.config import get_settings
from app.outcomes.inference import OutcomeInferenceEngine
from app.schemas.outcomes import OutcomePredictionRequest


def main() -> None:
    settings = get_settings()
    engine = OutcomeInferenceEngine(
        data_dir=settings.data_dir,
        processed_dir=settings.processed_data_dir,
        mappings_dir=settings.mappings_dir,
    )
    response = engine.predict(
        OutcomePredictionRequest(
            program_family="computer science",
            destination_country="United States",
            institution_tier=1,
        )
    )
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()
