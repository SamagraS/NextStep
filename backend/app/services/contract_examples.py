from uuid import NAMESPACE_URL, uuid5

from app.schemas.common import (
    BehavioralEngagement,
    DataCoverageLevel,
    DelayedPlacementFlag,
    MoratoriumWindow,
    RecommendationConfidence,
    ReliabilityBand,
    Tier,
    UniversityMatchStatus,
)
from app.schemas.auth import Token
from app.schemas.portfolio import (
    CohortAlert,
    CohortRow,
    PortfolioDashboardResponse,
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
    ScoreLatestResponse,
    ScoringResponse,
    TenacityBreakdown,
)
from app.schemas.student import (
    ActionPlanItem,
    MacroSummary,
    StudentDashboardResponse,
    TenacitySummary,
)
from app.utils.time import utc_now_iso

MOCK_TIMESTAMP = "2026-04-14T10:00:00Z"


def _deterministic_application_id(payload: OriginationScoringRequest) -> str:
    identity = "|".join(
        [
            payload.student_id or "anonymous",
            payload.full_name,
            payload.university_name,
            payload.program_name,
            payload.destination_country,
            payload.target_sector,
            str(payload.loan_amount_inr),
            str(payload.interest_rate_annual_pct),
            str(payload.repayment_term_months),
            str(payload.moratorium_months),
        ]
    )
    return str(uuid5(NAMESPACE_URL, identity))


def build_placeholder_scoring_response(payload: OriginationScoringRequest) -> ScoringResponse:
    tenacity_score = 0.79 if payload.student_id else None
    behavioral_engagement = (
        BehavioralEngagement.HIGH if tenacity_score is not None else BehavioralEngagement.NONE
    )

    return ScoringResponse(
        application_id=_deterministic_application_id(payload),
        placement_probability=PlacementProbability(
            p_3mo=0.42,
            p_6mo=0.68,
            p_12mo=0.81,
            monotonic_corrected=False,
            moratorium_window_used=MoratoriumWindow.six_months,
            moratorium_months=payload.moratorium_months,
        ),
        delayed_placement_risk=DelayedPlacementRisk(
            flag=DelayedPlacementFlag.MODERATE,
            reason="Placement is more likely after the moratorium window than within the first 3 months.",
            p3_p6_gap=0.26,
        ),
        salary_forecast=SalaryForecast(
            method="percentile_band_lookup",
            source_note="Placeholder lookup contract active until artifact-backed salary forecasting is integrated.",
            currency="USD_nominal",
            pessimistic=72000,
            realistic=91000,
            optimistic=112000,
            salary_progression_scenario=SalaryProgressionScenario(
                year_1=91000,
                year_2=98000,
                year_3=106000,
                basis="Seeded progression placeholder by program family.",
            ),
            emi_monthly_usd=1400,
            emi_as_pct_realistic=0.184,
        ),
        repayment_score=RepaymentScore(
            score=71,
            tier=Tier.GREEN,
            base_score_without_behavioral=68 if tenacity_score is not None else None,
            behavioral_boost_points=3 if tenacity_score is not None else None,
            employability_sub=0.68,
            affordability_sub=0.74,
            market_risk_sub=0.66,
            data_confidence_sub=0.78,
            moratorium_months_used=payload.moratorium_months,
        ),
        reliability=Reliability(
            band=ReliabilityBand.HIGH,
            behavioral_engagement=behavioral_engagement,
            tenacity_score=tenacity_score,
            tenacity_data_count=3 if tenacity_score is not None else 0,
            tenacity_breakdown=(
                TenacityBreakdown(
                    avg_completion_rate=1.0,
                    avg_engagement_depth=0.76,
                    avg_consistency=0.82,
                    certifications_verified=1,
                )
                if tenacity_score is not None
                else None
            ),
            imputation_flags=[],
            university_match=UniversityMatchStatus.resolved,
            university_match_score=100,
            data_coverage_level=DataCoverageLevel.HIGH,
            macro_snapshot_ts=MOCK_TIMESTAMP,
            stale_signal_warning=None,
        ),
        next_best_action=[
            NextBestAction(
                rank=1,
                action_type="skill_certification",
                title="Role-aligned Certification",
                rationale="Cloud engineering roles align well with the current placement outlook for this profile.",
                recommendation_confidence=RecommendationConfidence.high,
                ucb_raw=0.24,
                bandit_version="placeholder-v1",
            ),
            NextBestAction(
                rank=2,
                action_type="mock_interview",
                title="Interview Practice",
                rationale="Interview practice can improve short-horizon employability before the moratorium ends.",
                recommendation_confidence=RecommendationConfidence.medium,
                ucb_raw=0.44,
                bandit_version="placeholder-v1",
            ),
            NextBestAction(
                rank=3,
                action_type="networking_outreach",
                title="Alumni Networking Outreach",
                rationale="Targeted outreach helps convert placement probability into faster employer conversations.",
                recommendation_confidence=RecommendationConfidence.exploratory,
                ucb_raw=0.71,
                bandit_version="placeholder-v1",
            ),
        ],
        employer_match_list=[
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
        ],
        explanation=Explanation(
            tier_1="This profile shows a strong repayment outlook because expected placement timing aligns with the moratorium window and projected salary coverage looks healthy.",
            tier_2_positive=[
                "University Employability Ranking",
                "Target Sector Alignment",
                "Behavioral Engagement Signal",
            ],
            tier_2_risk=[
                "Early placement probability is lower than 6-month placement probability.",
                "Macro conditions are supportive but not neutral.",
            ],
            tier_2_attribution=ExplanationAttribution(
                base_rate=0.56,
                strength_multiplier=1.18,
                macro_adjustment=0.95,
                tenacity_boost=0.079 if tenacity_score is not None else None,
            ),
        ),
        model_metadata=ModelMetadata(
            model_version="contract-placeholder-v1",
            macro_snapshot_ts=MOCK_TIMESTAMP,
            training_data_cutoff="placeholder",
            l1_method="rule_based_placeholder",
            l2_method="lookup_placeholder",
            l3_method="weighted_formula",
            l4_method="bandit_placeholder",
        ),
    )


def build_placeholder_latest_score(application_id: str) -> ScoreLatestResponse:
    return ScoreLatestResponse(
        score=71,
        tier=Tier.GREEN,
        tenacity_score=0.79,
        behavioral_engagement=BehavioralEngagement.HIGH,
        scored_at=MOCK_TIMESTAMP,
    )


def build_placeholder_student_dashboard(student_id: str) -> StudentDashboardResponse:
    pending = [
        ActionPlanItem(
            action_id="action-1",
            action_type="skill_certification",
            title="AWS Cloud Fundamentals",
            rationale="This improves alignment with current cloud engineering demand in the US.",
            assigned_at=MOCK_TIMESTAMP,
            expected_effort_hours=14,
            total_active_seconds=14400,
            return_visits=4,
            certificate_uploaded=False,
            completed_at=None,
        ),
        ActionPlanItem(
            action_id="action-2",
            action_type="mock_interview",
            title="Mock Interview Practice",
            rationale="This helps convert realistic placement potential into interview readiness.",
            assigned_at=MOCK_TIMESTAMP,
            expected_effort_hours=2,
            total_active_seconds=3600,
            return_visits=1,
            certificate_uploaded=False,
            completed_at=None,
        ),
    ]

    completed = [
        ActionPlanItem(
            action_id="action-3",
            action_type="resume_improvement",
            title="Resume Improvement",
            rationale="This strengthens employer-readiness signals for technical roles.",
            assigned_at=MOCK_TIMESTAMP,
            expected_effort_hours=3,
            total_active_seconds=9000,
            return_visits=4,
            certificate_uploaded=False,
            completed_at=MOCK_TIMESTAMP,
        )
    ]

    return StudentDashboardResponse(
        readiness_score=71,
        action_plan=pending + completed,
        completed_actions=completed,
        pending_actions=pending,
        tenacity_summary=TenacitySummary(
            tenacity_score=0.79,
            behavioral_engagement="HIGH",
            data_points=3,
            summary="Strong pre-loan engagement across multiple actions and return visits.",
        ),
        macro_summary=MacroSummary(
            destination_country="United States",
            summary="Cloud engineering demand in the US is currently HIGH. Your action plan reflects this.",
            macro_snapshot_ts=MOCK_TIMESTAMP,
        ),
        employer_matches=[
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
        ],
    )


def build_placeholder_login_response() -> Token:
    return Token(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        token_type="bearer",
        role="student",
        full_name="Priya Sharma",
    )


def build_placeholder_cohort_list() -> list[CohortRow]:
    return [
        CohortRow(
            cohort_id="cohort-us-cs",
            program_name="MS Computer Science",
            destination_country="United States",
            cohort_size=43,
            baseline_score=72,
            current_score=68,
            delta=-4.0,
            severity="AMBER",
            triggered_at=MOCK_TIMESTAMP,
            primary_macro_driver="US tech hiring momentum softened.",
        )
    ]


def build_placeholder_alert_list() -> list[CohortAlert]:
    return [
        CohortAlert(
            cohort_id="cohort-us-cs",
            severity="AMBER",
            delta=-4.0,
            primary_macro_driver="US tech hiring momentum softened.",
            recommended_action="Rule-based: review employability support actions for this cohort.",
            macro_snapshot_ts=MOCK_TIMESTAMP,
            triggered_at=MOCK_TIMESTAMP,
        )
    ]


def build_placeholder_portfolio_dashboard() -> PortfolioDashboardResponse:
    return PortfolioDashboardResponse(
        total_active_cohorts=3,
        amber_count=1,
        red_count=1,
        cohorts=build_placeholder_cohort_list(),
        latest_alerts=build_placeholder_alert_list(),
    )
