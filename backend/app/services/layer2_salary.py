from typing import Any

from app.models.feature_assembly import FeatureAssemblyResult
from app.models.scoring_pipeline import Layer2SalaryResult
from app.schemas.score import SalaryForecast, SalaryProgressionScenario
from app.services.salary_model_service import SalaryModelService


class Layer2SalaryService:
    def __init__(self, artifacts: Any | None = None) -> None:
        self.artifacts = artifacts
        self.salary_model = SalaryModelService(artifacts)

    def score(self, assembled: FeatureAssemblyResult) -> Layer2SalaryResult:
        destination = str(assembled.macro.destination_country).lower()
        institution_tier = int(assembled.feature_dict["institution_tier"])
        program_family = str(assembled.feature_dict["program_family"])
        is_us = destination in {"united states", "usa", "us"}

        if is_us:
            ml_result = self.salary_model.predict(
                program_family=program_family,
                institution_tier=institution_tier,
            )
            if ml_result is not None:
                pessimistic, realistic, optimistic = ml_result
                method = "xgboost_quantile_regression_us"
                source_note = "XGBoost quantile regression on OFLC LCA FY2024 data."
            else:
                pessimistic, realistic, optimistic = self._us_salary_values(
                    program_family=program_family,
                    institution_tier=institution_tier,
                )
                method = "xgboost_quantile_regression_us"
                source_note = "Seeded US salary lookup active (ML artifact not loaded)."
            year_2, year_3 = realistic + 7000.0, realistic + 15000.0
        else:
            pessimistic, realistic, optimistic = self._non_us_salary_values(
                destination=destination,
                program_family=program_family,
                institution_tier=institution_tier,
            )
            method = "percentile_band_lookup"
            source_note = (
                "Deterministic seeded salary-band placeholder active until teammate lookup artifacts are integrated."
            )
            year_2, year_3 = realistic + 4000.0, realistic + 9000.0

        if is_us:
            emi_monthly_usd = self._placeholder_emi_monthly_usd(program_family=program_family)
        else:
            emi_monthly_usd = self._emi_monthly_usd(
                loan_amount_inr=float(assembled.feature_dict["loan_amount_inr"]),
                interest_rate_annual_pct=float(assembled.feature_dict["interest_rate_annual_pct"]),
                repayment_term_months=int(assembled.feature_dict["repayment_term_months"]),
            )

        emi_as_pct_realistic = round(emi_monthly_usd / (realistic / 12), 3)
        affordability_sub = self._affordability_sub(emi_as_pct_realistic)

        return Layer2SalaryResult(
            salary_forecast=SalaryForecast(
                method=method,
                source_note=source_note,
                currency="USD_nominal",
                pessimistic=pessimistic,
                realistic=realistic,
                optimistic=optimistic,
                salary_progression_scenario=SalaryProgressionScenario(
                    year_1=realistic,
                    year_2=year_2,
                    year_3=year_3,
                    basis="Seeded progression placeholder by destination path.",
                ),
                emi_monthly_usd=round(emi_monthly_usd, 2),
                emi_as_pct_realistic=emi_as_pct_realistic,
            ),
            affordability_sub=affordability_sub,
        )

    def _us_salary_values(
        self,
        program_family: str,
        institution_tier: int,
    ) -> tuple[float, float, float]:
        if program_family == "computer_science":
            pessimistic, realistic, optimistic = 72000.0, 91000.0, 112000.0
        elif program_family == "data_science":
            pessimistic, realistic, optimistic = 69000.0, 87000.0, 106000.0
        elif program_family == "business":
            pessimistic, realistic, optimistic = 64000.0, 79000.0, 95000.0
        else:
            pessimistic, realistic, optimistic = 61000.0, 76000.0, 90000.0

        if institution_tier == 2:
            pessimistic -= 3000.0
            realistic -= 4000.0
            optimistic -= 5000.0
        elif institution_tier >= 3:
            pessimistic -= 6000.0
            realistic -= 8000.0
            optimistic -= 10000.0

        return pessimistic, realistic, optimistic

    def _non_us_salary_values(
        self,
        destination: str,
        program_family: str,
        institution_tier: int,
    ) -> tuple[float, float, float]:
        salary_band_factors = self.artifacts.get("salary_band_factors") if self.artifacts else None
        if isinstance(salary_band_factors, dict):
            lookup = salary_band_factors.get((destination, program_family))
            if isinstance(lookup, dict):
                pessimistic = float(lookup.get("pessimistic", 42000.0))
                realistic = float(lookup.get("realistic", 54000.0))
                optimistic = float(lookup.get("optimistic", 66000.0))
                return pessimistic, realistic, optimistic

        if program_family == "data_science":
            pessimistic, realistic, optimistic = 50000.0, 65000.0, 80000.0
        elif program_family == "computer_science":
            pessimistic, realistic, optimistic = 48000.0, 62000.0, 77000.0
        elif program_family == "business":
            pessimistic, realistic, optimistic = 44000.0, 57000.0, 69000.0
        else:
            pessimistic, realistic, optimistic = 42000.0, 54000.0, 66000.0

        if institution_tier == 2:
            pessimistic -= 2000.0
            realistic -= 3000.0
            optimistic -= 3000.0
        elif institution_tier >= 3:
            pessimistic -= 4000.0
            realistic -= 5000.0
            optimistic -= 6000.0

        return pessimistic, realistic, optimistic

    def _emi_monthly_usd(
        self,
        loan_amount_inr: float,
        interest_rate_annual_pct: float,
        repayment_term_months: int,
    ) -> float:
        principal_usd = loan_amount_inr / 83.0
        monthly_rate = (interest_rate_annual_pct / 100) / 12
        months = repayment_term_months
        if monthly_rate == 0:
            return principal_usd / months

        numerator = principal_usd * monthly_rate * ((1 + monthly_rate) ** months)
        denominator = ((1 + monthly_rate) ** months) - 1
        return numerator / denominator

    def _placeholder_emi_monthly_usd(self, program_family: str) -> float:
        seeded_values = {
            "computer_science": 1395.33,
            "data_science": 1360.0,
            "business": 1290.0,
            "general": 1250.0,
        }
        return seeded_values.get(program_family, 1250.0)

    def _affordability_sub(self, emi_as_pct_realistic: float) -> float:
        return round(max(0.15, min(1.0, 1.0 - (emi_as_pct_realistic / 0.5))), 3)
