from app.core.config import get_settings
from app.outcomes.inference import OutcomeInferenceEngine


def main() -> None:
    settings = get_settings()
    engine = OutcomeInferenceEngine(
        data_dir=settings.data_dir,
        processed_dir=settings.processed_data_dir,
        mappings_dir=settings.mappings_dir,
    )
    engine.build_artifacts()
    print("Outcome pipeline artifacts built in data/processed")


if __name__ == "__main__":
    main()

