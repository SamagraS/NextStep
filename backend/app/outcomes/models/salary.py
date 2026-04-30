from __future__ import annotations

import numpy as np
import pandas as pd


try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover - optional dependency
    XGBRegressor = None


class SalaryModel:
    def build_lookup(self, salary_frame: pd.DataFrame, microdata_frame: pd.DataFrame) -> pd.DataFrame:
        aggregate_rows = self._build_non_us_lookup(salary_frame)
        us_rows = self._build_us_lookup(microdata_frame)
        return pd.concat([aggregate_rows, us_rows], ignore_index=True)

    def _build_us_lookup(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()

        families = sorted(frame["program_family"].dropna().unique())
        family_index = {family: index for index, family in enumerate(families)}
        working = frame.copy()
        working["family_code"] = working["program_family"].map(family_index)

        model_rows: list[dict[str, object]] = []
        if XGBRegressor is not None and len(working) >= 500:
            try:
                X = working[["family_code"]]
                y = working["annual_salary"]
                predictions: dict[str, np.ndarray] = {}
                for alpha, label in [(0.15, "p15"), (0.50, "p50"), (0.85, "p85")]:
                    model = XGBRegressor(
                        objective="reg:quantileerror",
                        quantile_alpha=alpha,
                        max_depth=4,
                        n_estimators=80,
                        learning_rate=0.08,
                        subsample=0.9,
                        colsample_bytree=1.0,
                        random_state=42,
                    )
                    model.fit(X, y)
                    predictions[label] = model.predict(
                        pd.DataFrame({"family_code": list(family_index.values())})
                    )
                for family, code in family_index.items():
                    p15 = float(predictions["p15"][code])
                    p50 = float(predictions["p50"][code])
                    p85 = float(predictions["p85"][code])
                    model_rows.extend(
                        self._tiered_salary_rows(
                            "United States",
                            family,
                            p15,
                            p50,
                            p85,
                            "xgboost_quantile_regression_us",
                        )
                    )
                return pd.DataFrame(model_rows)
            except Exception:
                pass

        grouped = working.groupby("program_family")["annual_salary"]
        for family, salaries in grouped:
            p15, p50, p85 = np.quantile(salaries, [0.15, 0.50, 0.85])
            model_rows.extend(self._tiered_salary_rows("United States", family, p15, p50, p85, "empirical_quantiles_us"))
        return pd.DataFrame(model_rows)

    def _build_non_us_lookup(self, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame()
        rows: list[dict[str, object]] = []
        for (country, program_family, institution_tier), chunk in frame.groupby(
            ["country", "program_family", "institution_tier"],
            dropna=False,
        ):
            median = float(chunk["salary_median"].median())
            p15 = float(chunk["salary_p15"].median()) if "salary_p15" in chunk.columns else np.nan
            p85 = float(chunk["salary_p85"].median()) if "salary_p85" in chunk.columns else np.nan
            if np.isnan(p15):
                p15 = median * 0.78
            if np.isnan(p85):
                p85 = median * 1.28
            currency = chunk["currency"].dropna().iloc[0] if chunk["currency"].notna().any() else "USD"
            rows.append(
                {
                    "country": country,
                    "program_family": program_family,
                    "institution_tier": int(institution_tier),
                    "p15": round(p15, 2),
                    "p50": round(median, 2),
                    "p85": round(max(p85, median), 2),
                    "currency": currency,
                    "method": "aggregate_lookup_with_heuristic_spread",
                }
            )
        return pd.DataFrame(rows)

    def _tiered_salary_rows(
        self,
        country: str,
        program_family: str,
        p15: float,
        p50: float,
        p85: float,
        method: str,
    ) -> list[dict[str, object]]:
        tier_factors = {1: 1.08, 2: 1.0, 3: 0.92}
        rows: list[dict[str, object]] = []
        for tier, factor in tier_factors.items():
            rows.append(
                {
                    "country": country,
                    "program_family": program_family,
                    "institution_tier": tier,
                    "p15": round(p15 * factor, 2),
                    "p50": round(p50 * factor, 2),
                    "p85": round(p85 * factor, 2),
                    "currency": "USD",
                    "method": method,
                }
            )
        return rows
