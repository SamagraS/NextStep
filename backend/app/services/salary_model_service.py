from typing import Any

import numpy as np


class SalaryModelService:
    """
    Wraps the three XGBoost quantile models (q15, q50, q85).
    Falls back gracefully to None when artifacts are not loaded.
    Feature vector order matches Colab training: [program_family, state_encoded, year, institution_tier]
    """

    DEFAULT_STATE = "CA"
    DEFAULT_YEAR = 2024

    FAMILY_FALLBACK: dict[str, int] = {
        "computer_science": 1,
        "data_science": 2,
        "business": 3,
        "general": 4,
    }

    def __init__(self, artifacts: Any | None = None) -> None:
        self._q15 = artifacts.get("salary_model_q15") if artifacts else None
        self._q50 = artifacts.get("salary_model_q50") if artifacts else None
        self._q85 = artifacts.get("salary_model_q85") if artifacts else None
        raw_state = artifacts.get("state_encode") if artifacts else None
        raw_family = artifacts.get("family_encode") if artifacts else None
        self._state_encode: dict[str, int] = raw_state if isinstance(raw_state, dict) else {}
        self._family_encode: dict[str, int] = raw_family if isinstance(raw_family, dict) else {}

    @property
    def available(self) -> bool:
        return all([
            self._q15 is not None,
            self._q50 is not None,
            self._q85 is not None,
            bool(self._state_encode),
            bool(self._family_encode),
        ])

    def predict(
        self,
        program_family: str,
        institution_tier: int,
        worksite_state: str = DEFAULT_STATE,
        year: int = DEFAULT_YEAR,
    ) -> tuple[float, float, float] | None:
        if not self.available:
            return None
        try:
            family_code = float(
                self._family_encode.get(program_family)
                or self.FAMILY_FALLBACK.get(program_family, 4)
            )
            state_code = float(self._state_encode.get(worksite_state.upper(), 0))
            x = np.array(
                [[family_code, state_code, float(year), float(institution_tier)]],
                dtype=float,
            )
            p15 = float(self._q15.predict(x)[0])
            p50 = float(self._q50.predict(x)[0])
            p85 = float(self._q85.predict(x)[0])
            # Enforce monotonicity and sanity bounds
            p15 = max(30_000.0, min(p15, 500_000.0))
            p50 = max(p15, min(p50, 500_000.0))
            p85 = max(p50, min(p85, 500_000.0))
            return p15, p50, p85
        except Exception:
            return None
