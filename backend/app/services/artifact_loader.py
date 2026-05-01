from dataclasses import dataclass
from pathlib import Path

import joblib

from app.schemas.health import ArtifactHealth


@dataclass(frozen=True)
class ArtifactContract:
    name: str
    filename: str
    source: str


ARTIFACT_CONTRACTS = [
    ArtifactContract("salary_model_q15", "salary_model_q15.pkl", "ml_artifact"),
    ArtifactContract("salary_model_q50", "salary_model_q50.pkl", "ml_artifact"),
    ArtifactContract("salary_model_q85", "salary_model_q85.pkl", "ml_artifact"),
    ArtifactContract("state_encode", "state_encode.pkl", "ml_artifact"),
    ArtifactContract("family_encode", "family_encode.pkl", "ml_artifact"),
    ArtifactContract("bandit_model", "bandit_model.pkl", "ml_artifact"),
    ArtifactContract("aggregate_outcomes", "aggregate_outcomes.pkl", "published_aggregate_data"),
    ArtifactContract("salary_band_factors", "salary_band_factors.pkl", "published_salary_band_data"),
    ArtifactContract("university_lookup", "university_lookup.pkl", "integration_dataset"),
    ArtifactContract("taxonomy_map", "taxonomy_map.pkl", "integration_dataset"),
]


class ArtifactRegistry:
    def __init__(self, artifacts_dir: Path) -> None:
        self.artifacts_dir = artifacts_dir
        self._artifacts: dict[str, object] = {}
        self._status: list[ArtifactHealth] = []

    def load(self) -> None:
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        statuses: list[ArtifactHealth] = []

        for contract in ARTIFACT_CONTRACTS:
            expected_path = self.artifacts_dir / contract.filename
            if expected_path.exists():
                try:
                    self._artifacts[contract.name] = joblib.load(expected_path)
                    statuses.append(
                        ArtifactHealth(
                            name=contract.name,
                            expected_path=expected_path,
                            loaded=True,
                            source=contract.source,
                            detail="loaded",
                        )
                    )
                except Exception as exc:
                    self._artifacts[contract.name] = None
                    statuses.append(
                        ArtifactHealth(
                            name=contract.name,
                            expected_path=expected_path,
                            loaded=False,
                            source=contract.source,
                            detail=f"load_failed: {exc.__class__.__name__}",
                        )
                    )
            else:
                self._artifacts[contract.name] = None
                statuses.append(
                    ArtifactHealth(
                        name=contract.name,
                        expected_path=expected_path,
                        loaded=False,
                        source=contract.source,
                        detail="missing_placeholder_active",
                    )
                )

        self._status = statuses

    def get(self, name: str) -> object | None:
        return self._artifacts.get(name)

    def snapshot(self) -> list[ArtifactHealth]:
        return list(self._status)
