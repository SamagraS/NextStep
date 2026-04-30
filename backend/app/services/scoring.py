from uuid import NAMESPACE_URL, uuid5

from app.schemas.common import (
    DataCoverageLevel,
    DelayedPlacementFlag,
    MoratoriumWindow,
    RecommendationConfidence,
    ReliabilityBand,
    Tier,
)
from app.schemas.score import (
    DelayedPlacementRisk,
    EmployerMatch,
    Explanation,
    ExplanationAttribution,
    ModelMetadata,
    NextBestAction,
    OriginationScoringRequest,
    PlacementProbability,
    Reliability,
    RepaymentScore,
    SalaryForecast,
    SalaryProgressionScenario,
    ScoringResponse,
)
from app.services.demo_store import DemoStore, MOCK_ACTION_COMPLETION_TS, MOCK_SNAPSHOT_TS
from app.services.feature_assembly import FeatureAssemblyService


class DemoScoringService:
    def __init__(self, store: DemoStore, artifacts=None) -> None:
        self.store = store
        self.feature_assembly = FeatureAssemblyService(store=store, artifacts=artifacts)

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

    def _build_response(self, payload: OriginationScoringRequest) -> ScoringResponse:
        application_id = self._deterministic_application_id(payload)
        assembled = self.feature_assembly.assemble(payload)
        student = self.store.get_student(payload.student_id) if payload.student_id else None

        salary = self._salary_forecast(assembled)
        p_without_behavioral = self._placement_probability(assembled, tenacity_score=None)
        p_with_behavioral = self._placement_probability(
            assembled, tenacity_score=assembled.tenacity.tenacity_score
        )

        employability_base = self._moratorium_relative_probability(
            moratorium_months=int(assembled.feature_dict["moratorium_months"]),
            placement=p_without_behavioral,
        )
        employability_final = self._moratorium_relative_probability(
            moratorium_months=int(assembled.feature_dict["moratorium_months"]),
            placement=p_with_behavioral,
        )
        affordability_sub = self._affordability_sub(salary.emi_as_pct_realistic)
        market_risk_sub = assembled.macro.market_risk_sub
        imputation_flags = assembled.imputation_flags
        data_confidence_sub = self._data_confidence_sub(imputation_flags)

        base_score = int(
            round(
                (
                    0.35 * employability_base
                    + 0.30 * affordability_sub
                    + 0.20 * market_risk_sub
                    + 0.15 * data_confidence_sub
                )
                * 100
            )
        )
        completion_bonus_points = (
            self.store.get_score_delta_points(student.student_id)
            if student is not None
            else 0
        )
        scaled_base_score = max(0, min(int(round(base_score * 0.79)), 100))
        behavioral_boost_points = None
        if assembled.tenacity.tenacity_score is not None:
            behavioral_boost_points = (
                min(int(round(assembled.tenacity.tenacity_score * 4)), 3)
                + completion_bonus_points
            )

        final_score = scaled_base_score + (behavioral_boost_points or 0)
        final_score = max(0, min(final_score, 100))

        tier = self._tier(final_score)

        delayed = self._delayed_placement_risk(p_with_behavioral.p_3mo, p_with_behavioral.p_6mo)
        explanation = self._explanation(
            tier=tier,
            delayed_flag=delayed.flag,
            tenacity_score=assembled.tenacity.tenacity_score,
        )

        return ScoringResponse(
            application_id=application_id,
            placement_probability=p_with_behavioral,
            delayed_placement_risk=delayed,
            salary_forecast=salary,
            repayment_score=RepaymentScore(
                score=final_score,
                tier=tier,
                base_score_without_behavioral=(
                    scaled_base_score if assembled.tenacity.tenacity_score is not None else None
                ),
                behavioral_boost_points=behavioral_boost_points,
                employability_sub=employability_final,
                affordability_sub=affordability_sub,
                market_risk_sub=market_risk_sub,
                data_confidence_sub=data_confidence_sub,
                moratorium_months_used=int(assembled.feature_dict["moratorium_months"]),
            ),
            reliability=Reliability(
                band=self._reliability_band(imputation_flags),
                behavioral_engagement=assembled.tenacity.behavioral_engagement,
                tenacity_score=assembled.tenacity.tenacity_score,
                tenacity_data_count=assembled.tenacity.data_count,
                tenacity_breakdown=assembled.tenacity.breakdown,
                imputation_flags=imputation_flags,
                university_match=assembled.university.match_status,
                university_match_score=assembled.university.match_score,
                data_coverage_level=self._coverage_level(imputation_flags),
                macro_snapshot_ts=assembled.macro.macro_snapshot_ts,
                stale_signal_warning=assembled.macro.stale_signal_warning,
            ),
            next_best_action=self._next_best_actions(
                weakest_subscore=min(
                    {
                        "employability": employability_final,
                        "affordability": affordability_sub,
                        "market_risk": market_risk_sub,
                        "data_confidence": data_confidence_sub,
                    },
                    key=lambda item: {
                        "employability": employability_final,
                        "affordability": affordability_sub,
                        "market_risk": market_risk_sub,
                        "data_confidence": data_confidence_sub,
                    }[item],
                )
            ),
            employer_match_list=self._employer_matches(
                destination_country=assembled.macro.destination_country,
                program_family=str(assembled.feature_dict["program_family"]),
            ),
            explanation=explanation,
            model_metadata=ModelMetadata(
                model_version="demo-rule-based-v1",
                macro_snapshot_ts=assembled.macro.macro_snapshot_ts,
                training_data_cutoff="placeholder",
                l1_method="rule_based_demo_placeholder",
                l2_method="seeded_salary_lookup",
                l3_method="weighted_formula",
                l4_method="rule_based_bandit_placeholder",
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

    def _placement_probability(
        self, assembled, tenacity_score: float | None
    ) -> PlacementProbability:
        cgpa_value = float(assembled.cgpa.resolved_value or 7.0)
        internship_value = int(assembled.internship_count.resolved_value or 0)
        cgpa_adj = (cgpa_value - 7.0) * 0.03
        internship_adj = min(internship_value, 3) * 0.03
        sector_adj = 0.03 if "cloud" in str(assembled.feature_dict["target_sector"]).lower() else 0.01
        institution_adj = {1: 0.0, 2: -0.02, 3: -0.04}.get(
            int(assembled.feature_dict["institution_tier"]), -0.04
        )
        program_family = str(assembled.feature_dict["program_family"])
        if program_family == "computer_science":
            program_adj = 0.0
        elif program_family == "data_science":
            program_adj = -0.01
        elif program_family == "business":
            program_adj = -0.02
        else:
            program_adj = -0.03
        behavior_adj = (tenacity_score or 0.0) * 0.04
        p_3mo = max(
            0.18,
            min(
                0.75,
                0.36
                + cgpa_adj
                + internship_adj
                + sector_adj
                + institution_adj
                + program_adj
                + behavior_adj,
            ),
        )
        p_6mo = max(p_3mo, min(0.92, p_3mo + 0.22))
        p_12mo = max(p_6mo, min(0.98, p_6mo + 0.13))

        return PlacementProbability(
            p_3mo=round(p_3mo, 3),
            p_6mo=round(p_6mo, 3),
            p_12mo=round(p_12mo, 3),
            monotonic_corrected=False,
            moratorium_window_used=self._moratorium_window(int(assembled.feature_dict["moratorium_months"])),
            moratorium_months=int(assembled.feature_dict["moratorium_months"]),
        )

    def _moratorium_window(self, moratorium_months: int) -> MoratoriumWindow:
        if moratorium_months <= 3:
            return MoratoriumWindow.three_months
        if moratorium_months <= 6:
            return MoratoriumWindow.six_months
        return MoratoriumWindow.twelve_months

    def _moratorium_relative_probability(
        self, moratorium_months: int, placement: PlacementProbability
    ) -> float:
        window = self._moratorium_window(moratorium_months)
        if window == MoratoriumWindow.three_months:
            return placement.p_3mo
        if window == MoratoriumWindow.six_months:
            return placement.p_6mo
        return placement.p_12mo

    def _salary_forecast(self, assembled) -> SalaryForecast:
        destination = assembled.macro.destination_country.lower()
        institution_tier = int(assembled.feature_dict["institution_tier"])
        program_family = str(assembled.feature_dict["program_family"])
        is_us = destination in {"united states", "usa", "us"}
        if is_us:
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
            method = "xgboost_quantile_regression_us"
            source_note = "Deterministic seeded US salary placeholder active until artifact-backed inference is integrated."
            year_2, year_3 = realistic + 7000.0, realistic + 15000.0
        else:
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
            method = "percentile_band_lookup"
            source_note = "Deterministic seeded salary-band placeholder active until teammate lookup artifacts are integrated."
            year_2, year_3 = realistic + 4000.0, realistic + 9000.0

        emi_monthly_usd = self._emi_monthly_usd(
            loan_amount_inr=float(assembled.feature_dict["loan_amount_inr"]),
            interest_rate_annual_pct=float(assembled.feature_dict["interest_rate_annual_pct"]),
            repayment_term_months=int(assembled.feature_dict["repayment_term_months"]),
        )
        return SalaryForecast(
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
            emi_as_pct_realistic=round(emi_monthly_usd / realistic, 3),
        )

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

    def _affordability_sub(self, emi_as_pct_realistic: float) -> float:
        return max(0.15, min(1.0, 1.0 - (emi_as_pct_realistic / 0.5)))

    def _data_confidence_sub(self, imputation_flags: list[str]) -> float:
        return max(0.45, 0.88 - (0.1 * len(imputation_flags)))

    def _tier(self, score: int) -> Tier:
        if score >= 65:
            return Tier.GREEN
        if score >= 40:
            return Tier.AMBER
        return Tier.RED

    def _delayed_placement_risk(self, p_3mo: float, p_6mo: float) -> DelayedPlacementRisk:
        gap = round(p_6mo - p_3mo, 3)
        if gap >= 0.3:
            flag = DelayedPlacementFlag.HIGH
            reason = "Most placement momentum appears after the early post-graduation window."
        elif gap >= 0.18:
            flag = DelayedPlacementFlag.MODERATE
            reason = "Placement is more likely after the moratorium window than within the first 3 months."
        else:
            flag = DelayedPlacementFlag.LOW
            reason = "Early and medium-horizon placement probabilities are closely aligned."
        return DelayedPlacementRisk(flag=flag, reason=reason, p3_p6_gap=gap)

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

    def _next_best_actions(self, weakest_subscore: str) -> list[NextBestAction]:
        if weakest_subscore == "employability":
            actions = [
                ("skill_certification", "Role-aligned certification is the strongest immediate lever for this placement profile.", RecommendationConfidence.high, 0.24),
                ("mock_interview", "Interview practice improves short-horizon conversion before the moratorium window ends.", RecommendationConfidence.medium, 0.44),
                ("networking_outreach", "Targeted outreach can accelerate employer conversations for this profile.", RecommendationConfidence.exploratory, 0.71),
            ]
        elif weakest_subscore == "affordability":
            actions = [
                ("networking_outreach", "Faster placement timing helps reduce affordability pressure by improving income visibility.", RecommendationConfidence.high, 0.28),
                ("resume_improvement", "Sharper positioning improves employer response quality for the current salary band.", RecommendationConfidence.medium, 0.49),
                ("mock_interview", "Interview readiness can shorten time-to-offer for this profile.", RecommendationConfidence.exploratory, 0.64),
            ]
        else:
            actions = [
                ("skill_certification", "This action is well-supported by similar profiles in the seeded demo state.", RecommendationConfidence.high, 0.24),
                ("mock_interview", "This action can improve placement timing within the current market window.", RecommendationConfidence.medium, 0.44),
                ("portfolio_project", "This action is exploratory but promising for strengthening technical employer evidence.", RecommendationConfidence.exploratory, 0.69),
            ]

        return [
            NextBestAction(
                rank=index + 1,
                action_type=action_type,
                rationale=rationale,
                recommendation_confidence=confidence,
                ucb_raw=ucb_raw,
                bandit_version="demo-placeholder-v1",
            )
            for index, (action_type, rationale, confidence, ucb_raw) in enumerate(actions)
        ]

    def _employer_matches(self, destination_country: str, program_family: str) -> list[EmployerMatch]:
        destination = destination_country.lower()
        if destination in {"united states", "usa", "us"}:
            if program_family == "business":
                return [
                    EmployerMatch(employer="Deloitte", median_salary_usd=118000, annual_h1b_filings=940, visa_approval_rate=0.88),
                    EmployerMatch(employer="PwC", median_salary_usd=114000, annual_h1b_filings=520, visa_approval_rate=0.84),
                    EmployerMatch(employer="KPMG", median_salary_usd=112000, annual_h1b_filings=470, visa_approval_rate=0.83),
                    EmployerMatch(employer="EY", median_salary_usd=113000, annual_h1b_filings=455, visa_approval_rate=0.82),
                    EmployerMatch(employer="Accenture", median_salary_usd=116000, annual_h1b_filings=870, visa_approval_rate=0.86),
                ]
            return [
                EmployerMatch(employer="Amazon", median_salary_usd=132000, annual_h1b_filings=1840, visa_approval_rate=0.92),
                EmployerMatch(employer="Microsoft", median_salary_usd=128000, annual_h1b_filings=1610, visa_approval_rate=0.94),
                EmployerMatch(employer="Deloitte", median_salary_usd=118000, annual_h1b_filings=940, visa_approval_rate=0.88),
                EmployerMatch(employer="Accenture", median_salary_usd=116000, annual_h1b_filings=870, visa_approval_rate=0.86),
                EmployerMatch(employer="Google", median_salary_usd=145000, annual_h1b_filings=790, visa_approval_rate=0.95),
            ]
        return [
            EmployerMatch(employer="Deloitte", median_salary_usd=74000, annual_h1b_filings=120, visa_approval_rate=0.84),
            EmployerMatch(employer="Accenture", median_salary_usd=72000, annual_h1b_filings=100, visa_approval_rate=0.83),
            EmployerMatch(employer="Capgemini", median_salary_usd=69000, annual_h1b_filings=88, visa_approval_rate=0.81),
            EmployerMatch(employer="PwC", median_salary_usd=71000, annual_h1b_filings=76, visa_approval_rate=0.82),
            EmployerMatch(employer="KPMG", median_salary_usd=70000, annual_h1b_filings=61, visa_approval_rate=0.8),
        ]

    def _explanation(
        self, tier: Tier, delayed_flag: DelayedPlacementFlag, tenacity_score: float | None
    ) -> Explanation:
        if tier == Tier.GREEN:
            tier_1 = "This profile shows a strong repayment outlook because placement timing and salary coverage remain supportive relative to the moratorium window."
        elif tier == Tier.AMBER:
            tier_1 = "This profile is workable but needs targeted support because repayment confidence depends on improving placement timing and execution."
        else:
            tier_1 = "This profile currently carries elevated repayment risk because early placement and affordability support are not strong enough yet."

        positives = ["University Employability Ranking", "Target Sector Alignment"]
        if tenacity_score is not None:
            positives.append("Behavioral Engagement Signal")

        risks = []
        if delayed_flag != DelayedPlacementFlag.LOW:
            risks.append("Early placement probability trails the later employment window.")
        risks.append("Macro conditions are supportive but not neutral.")

        return Explanation(
            tier_1=tier_1,
            tier_2_positive=positives,
            tier_2_risk=risks,
            tier_2_attribution=ExplanationAttribution(
                base_rate=0.56,
                strength_multiplier=1.18 if tenacity_score is not None else 1.10,
                macro_adjustment=0.95,
                tenacity_boost=round((tenacity_score or 0) * 0.10, 3) if tenacity_score is not None else None,
            ),
        )
