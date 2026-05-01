from uuid import NAMESPACE_URL, uuid5

from app.models.feature_assembly import FeatureAssemblyResult
from app.schemas.common import (
    DataCoverageLevel,
    DelayedPlacementFlag,
    ReliabilityBand,
)
from app.schemas.score import (
    EmployerMatch,
    Explanation,
    ExplanationAttribution,
    ModelMetadata,
    OriginationScoringRequest,
    Reliability,
    ScoringResponse,
)
from app.services.demo_store import DemoStore, MOCK_ACTION_COMPLETION_TS, MOCK_SNAPSHOT_TS
from app.services.feature_assembly import FeatureAssemblyService
from app.services.layer1_placement import Layer1PlacementService
from app.services.layer2_salary import Layer2SalaryService
from app.services.layer3_repayment import Layer3RepaymentService
from app.services.layer4_recommendation import Layer4RecommendationService


class DemoScoringService:
    def __init__(self, store: DemoStore, artifacts=None) -> None:
        self.store = store
        self.artifacts = artifacts
        self.feature_assembly = FeatureAssemblyService(store=store, artifacts=artifacts)
        self.layer1 = Layer1PlacementService(artifacts=artifacts)
        self.layer2 = Layer2SalaryService(artifacts=artifacts)
        self.layer3 = Layer3RepaymentService()
        self.layer4 = Layer4RecommendationService(artifacts=artifacts)

    def score_origination(self, payload: OriginationScoringRequest) -> tuple[ScoringResponse, str]:
        response = self._build_response(payload)
        scored_at = MOCK_SNAPSHOT_TS
        self.store.save_application(
            application_id=response.application_id,
            student_id=payload.student_id,
            payload=payload,
            response=response,
            scored_at=scored_at,
        )
        return response, scored_at

    def rebuild_application(self, application_id: str) -> ScoringResponse | None:
        application = self.store.get_application(application_id)
        if application is None:
            return None

        response = self._build_response(application.payload)
        self.store.save_application(
            application_id=application_id,
            student_id=application.student_id,
            payload=application.payload,
            response=response.model_copy(update={"application_id": application_id}),
            scored_at=MOCK_ACTION_COMPLETION_TS,
        )
        return self.store.get_application(application_id).response

    def build_employer_matches(
        self,
        destination_country: str,
        program_family: str,
    ) -> list[EmployerMatch]:
        destination = destination_country.lower()
        if destination in {"united states", "usa", "us"}:
            if program_family == "business":
                return [
                    EmployerMatch(
                        employer="Deloitte",
                        median_salary_usd=118000,
                        annual_h1b_filings=940,
                        visa_approval_rate=0.88,
                    ),
                    EmployerMatch(
                        employer="PwC",
                        median_salary_usd=114000,
                        annual_h1b_filings=520,
                        visa_approval_rate=0.84,
                    ),
                    EmployerMatch(
                        employer="KPMG",
                        median_salary_usd=112000,
                        annual_h1b_filings=470,
                        visa_approval_rate=0.83,
                    ),
                    EmployerMatch(
                        employer="EY",
                        median_salary_usd=113000,
                        annual_h1b_filings=455,
                        visa_approval_rate=0.82,
                    ),
                    EmployerMatch(
                        employer="Accenture",
                        median_salary_usd=116000,
                        annual_h1b_filings=870,
                        visa_approval_rate=0.86,
                    ),
                ]
            return [
                EmployerMatch(
                    employer="Amazon",
                    median_salary_usd=132000,
                    annual_h1b_filings=1840,
                    visa_approval_rate=0.92,
                ),
                EmployerMatch(
                    employer="Microsoft",
                    median_salary_usd=128000,
                    annual_h1b_filings=1610,
                    visa_approval_rate=0.94,
                ),
                EmployerMatch(
                    employer="Deloitte",
                    median_salary_usd=118000,
                    annual_h1b_filings=940,
                    visa_approval_rate=0.88,
                ),
                EmployerMatch(
                    employer="Accenture",
                    median_salary_usd=116000,
                    annual_h1b_filings=870,
                    visa_approval_rate=0.86,
                ),
                EmployerMatch(
                    employer="Google",
                    median_salary_usd=145000,
                    annual_h1b_filings=790,
                    visa_approval_rate=0.95,
                ),
            ]

        return [
            EmployerMatch(
                employer="Deloitte",
                median_salary_usd=74000,
                annual_h1b_filings=120,
                visa_approval_rate=0.84,
            ),
            EmployerMatch(
                employer="Accenture",
                median_salary_usd=72000,
                annual_h1b_filings=100,
                visa_approval_rate=0.83,
            ),
            EmployerMatch(
                employer="Capgemini",
                median_salary_usd=69000,
                annual_h1b_filings=88,
                visa_approval_rate=0.81,
            ),
            EmployerMatch(
                employer="PwC",
                median_salary_usd=71000,
                annual_h1b_filings=76,
                visa_approval_rate=0.82,
            ),
            EmployerMatch(
                employer="KPMG",
                median_salary_usd=70000,
                annual_h1b_filings=61,
                visa_approval_rate=0.8,
            ),
        ]

    def _build_response(self, payload: OriginationScoringRequest) -> ScoringResponse:
        application_id = self._deterministic_application_id(payload)
        assembled = self.feature_assembly.assemble(payload)
        student = self.store.get_student(payload.student_id) if payload.student_id else None
        completion_bonus_points = (
            self.store.get_score_delta_points(student.student_id)
            if student is not None
            else 0
        )
        data_confidence_sub = self._data_confidence_sub(assembled.imputation_flags)

        layer1_result = self.layer1.score(assembled)
        layer2_result = self.layer2.score(assembled)
        layer3_result = self.layer3.score(
            placement=layer1_result,
            salary=layer2_result,
            market_risk_sub=assembled.macro.market_risk_sub,
            data_confidence_sub=data_confidence_sub,
            moratorium_months=int(assembled.feature_dict["moratorium_months"]),
            tenacity_score=assembled.tenacity.tenacity_score,
            completion_bonus_points=completion_bonus_points,
        )
        layer4_result = self.layer4.recommend(
            assembled=assembled,
            placement_probability_6mo=layer1_result.placement_probability.p_6mo,
            weakest_subscore=layer3_result.weakest_subscore,
        )

        return ScoringResponse(
            application_id=application_id,
            placement_probability=layer1_result.placement_probability,
            delayed_placement_risk=layer1_result.delayed_placement_risk,
            salary_forecast=layer2_result.salary_forecast,
            repayment_score=layer3_result.repayment_score,
            reliability=Reliability(
                band=self._reliability_band(assembled.imputation_flags),
                behavioral_engagement=assembled.tenacity.behavioral_engagement,
                tenacity_score=assembled.tenacity.tenacity_score,
                tenacity_data_count=assembled.tenacity.data_count,
                tenacity_breakdown=assembled.tenacity.breakdown,
                imputation_flags=assembled.imputation_flags,
                university_match=assembled.university.match_status,
                university_match_score=assembled.university.match_score,
                data_coverage_level=self._coverage_level(assembled.imputation_flags),
                macro_snapshot_ts=assembled.macro.macro_snapshot_ts,
                stale_signal_warning=assembled.macro.stale_signal_warning,
            ),
            next_best_action=layer4_result.next_best_actions,
            employer_match_list=self.build_employer_matches(
                destination_country=assembled.macro.destination_country,
                program_family=str(assembled.feature_dict["program_family"]),
            ),
            explanation=self._explanation(
                assembled=assembled,
                delayed_flag=layer1_result.delayed_placement_risk.flag,
                base_rate=layer1_result.base_rate,
                strength_multiplier=layer1_result.strength_multiplier,
                macro_adjustment=layer1_result.macro_adjustment,
                tenacity_boost=layer1_result.tenacity_boost,
                final_score=layer3_result.repayment_score.score,
            ),
            model_metadata=ModelMetadata(
                model_version="demo-rule-based-v2",
                macro_snapshot_ts=assembled.macro.macro_snapshot_ts,
                training_data_cutoff="placeholder",
                l1_method="rule_based_placement_scorecard",
                l2_method="seeded_salary_lookup_with_us_fallback",
                l3_method="weighted_formula",
                l4_method="linucb_placeholder_with_priya_fallback",
            ),
        )

    def _deterministic_application_id(self, payload: OriginationScoringRequest) -> str:
        identity = "|".join(
            [
                payload.student_id or "anonymous",
                payload.full_name,
                payload.university_name,
                payload.program_name,
                payload.destination_country,
                payload.target_sector,
                str(payload.cgpa_present),
                str(payload.cgpa),
                str(payload.internship_count_present),
                str(payload.internship_count),
                str(payload.stem_opt_eligible_present),
                str(payload.stem_opt_eligible),
                str(payload.loan_amount_inr),
                str(payload.interest_rate_annual_pct),
                str(payload.repayment_term_months),
                str(payload.moratorium_months),
            ]
        )
        return str(uuid5(NAMESPACE_URL, identity))

    def _data_confidence_sub(self, imputation_flags: list[str]) -> float:
        return round(max(0.45, 0.88 - (0.1 * len(imputation_flags))), 3)

    def _coverage_level(self, imputation_flags: list[str]) -> DataCoverageLevel:
        if len(imputation_flags) == 0:
            return DataCoverageLevel.HIGH
        if len(imputation_flags) == 1:
            return DataCoverageLevel.MEDIUM
        return DataCoverageLevel.LOW

    def _reliability_band(self, imputation_flags: list[str]) -> ReliabilityBand:
        if len(imputation_flags) == 0:
            return ReliabilityBand.HIGH
        if len(imputation_flags) == 1:
            return ReliabilityBand.MEDIUM
        return ReliabilityBand.LOW

    def _explanation(
        self,
        assembled: FeatureAssemblyResult,
        delayed_flag: DelayedPlacementFlag,
        base_rate: float,
        strength_multiplier: float,
        macro_adjustment: float,
        tenacity_boost: float | None,
        final_score: int,
    ) -> Explanation:
        if final_score >= 65:
            tier_1 = (
                "This profile shows a strong repayment outlook because placement timing and salary coverage remain supportive relative to the moratorium window."
            )
        elif final_score >= 40:
            tier_1 = (
                "This profile is workable but needs targeted support because repayment confidence depends on improving placement timing and execution."
            )
        else:
            tier_1 = (
                "This profile currently carries elevated repayment risk because early placement and affordability support are not strong enough yet."
            )

        positives = ["University Employability Ranking", "Target Sector Alignment"]
        if assembled.tenacity.tenacity_score is not None:
            positives.append("Behavioral Engagement Signal")

        risks: list[str] = []
        if delayed_flag != DelayedPlacementFlag.LOW:
            risks.append("Early placement probability trails the later employment window.")
        if str(assembled.feature_dict["program_family"]) == "general":
            risks.append("Program taxonomy is running on fallback mapping for this profile.")
        risks.append("Macro conditions are supportive but not neutral.")

        return Explanation(
            tier_1=tier_1,
            tier_2_positive=positives,
            tier_2_risk=risks,
            tier_2_attribution=ExplanationAttribution(
                base_rate=base_rate,
                strength_multiplier=strength_multiplier,
                macro_adjustment=macro_adjustment,
                tenacity_boost=tenacity_boost,
            ),
        )
