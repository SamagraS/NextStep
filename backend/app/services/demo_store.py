from dataclasses import dataclass, field

from app.schemas.common import BehavioralEngagement, Tier
from app.schemas.health import SSEStudentProfileUpdatedEvent
from app.schemas.score import OriginationScoringRequest, ScoringResponse

MOCK_SNAPSHOT_TS = "2026-04-14T10:00:00Z"
MOCK_ACTION_COMPLETION_TS = "2026-04-14T10:05:00Z"


@dataclass
class DemoPreloanAction:
    title: str
    action_type: str
    total_active_seconds: int
    days_spread: int
    return_visits: int
    certificate_uploaded: bool


@dataclass
class DemoDashboardAction:
    action_id: str
    action_type: str
    title: str
    rationale: str
    assigned_at: str
    expected_effort_hours: float
    total_active_seconds: int
    return_visits: int
    certificate_uploaded: bool
    status: str
    completed_at: str | None = None
    readiness_score_delta: int = 0


@dataclass(frozen=True)
class DashboardActionCompletionResult:
    student_found: bool
    action_found: bool
    changed: bool
    action: DemoDashboardAction | None = None


@dataclass
class DemoStudentState:
    student_id: str
    full_name: str
    destination_country: str
    program_family: str
    macro_summary: str
    readiness_base_score: int
    preloan_actions: list[DemoPreloanAction] = field(default_factory=list)
    dashboard_actions: list[DemoDashboardAction] = field(default_factory=list)


@dataclass
class DemoApplicationState:
    application_id: str
    student_id: str | None
    payload: OriginationScoringRequest
    response: ScoringResponse
    scored_at: str


@dataclass
class DemoCohortAlert:
    alert_id: str
    cohort_id: str
    severity: str
    delta: float
    primary_macro_driver: str
    recommended_action: str
    macro_snapshot_ts: str
    created_at: str


@dataclass
class DemoCohortState:
    cohort_id: str
    program_name: str
    destination_country: str
    cohort_size: int
    baseline_score: float
    current_score: float


class DemoStore:
    def __init__(self) -> None:
        self.students: dict[str, DemoStudentState] = {}
        self.applications: dict[str, DemoApplicationState] = {}
        self.student_to_application_ids: dict[str, set[str]] = {}
        self.cohorts: dict[str, DemoCohortState] = {}
        self.cohort_alerts: dict[str, DemoCohortAlert] = {}
        self.latest_events: dict[str, SSEStudentProfileUpdatedEvent] = {}
        self.portfolio_rescore_triggered = False
        self._seed()

    def _seed(self) -> None:
        self.students["student-priya"] = DemoStudentState(
            student_id="student-priya",
            full_name="Priya Sharma",
            destination_country="United States",
            program_family="computer_science",
            macro_summary="Cloud engineering demand in the US is currently HIGH. Your action plan reflects this.",
            readiness_base_score=67,
            preloan_actions=[
                DemoPreloanAction(
                    title="AWS Cloud Fundamentals",
                    action_type="skill_certification",
                    total_active_seconds=14 * 3600,
                    days_spread=8,
                    return_visits=11,
                    certificate_uploaded=True,
                ),
                DemoPreloanAction(
                    title="Resume Improvement",
                    action_type="resume_improvement",
                    total_active_seconds=int(2.5 * 3600),
                    days_spread=3,
                    return_visits=4,
                    certificate_uploaded=False,
                ),
                DemoPreloanAction(
                    title="Mock Interview",
                    action_type="mock_interview",
                    total_active_seconds=int(1.8 * 3600),
                    days_spread=1,
                    return_visits=1,
                    certificate_uploaded=False,
                ),
            ],
            dashboard_actions=[
                DemoDashboardAction(
                    action_id="action-assign-1",
                    action_type="skill_certification",
                    title="Kubernetes Certification Sprint",
                    rationale="This improves fit for cloud engineering roles before the moratorium window ends.",
                    assigned_at=MOCK_SNAPSHOT_TS,
                    expected_effort_hours=6,
                    total_active_seconds=0,
                    return_visits=0,
                    certificate_uploaded=False,
                    status="assigned",
                    readiness_score_delta=3,
                ),
                DemoDashboardAction(
                    action_id="action-assign-2",
                    action_type="networking_outreach",
                    title="Alumni Networking Outreach",
                    rationale="Targeted outreach can speed up employer conversations for this profile.",
                    assigned_at=MOCK_SNAPSHOT_TS,
                    expected_effort_hours=4,
                    total_active_seconds=0,
                    return_visits=0,
                    certificate_uploaded=False,
                    status="assigned",
                    readiness_score_delta=2,
                ),
                DemoDashboardAction(
                    action_id="action-assign-3",
                    action_type="portfolio_project",
                    title="Cloud Portfolio Project",
                    rationale="A concrete project strengthens employer evidence for technical roles.",
                    assigned_at=MOCK_SNAPSHOT_TS,
                    expected_effort_hours=10,
                    total_active_seconds=0,
                    return_visits=0,
                    certificate_uploaded=False,
                    status="assigned",
                    readiness_score_delta=4,
                ),
            ],
        )

        self.students["student-aravind"] = DemoStudentState(
            student_id="student-aravind",
            full_name="Aravind Nair",
            destination_country="Australia",
            program_family="computer_science",
            macro_summary="Engineering demand in Australia remains STABLE with moderate growth in regional hubs.",
            readiness_base_score=62,
            preloan_actions=[
                DemoPreloanAction(
                    title="Civil Engineering Basics",
                    action_type="skill_certification",
                    total_active_seconds=8 * 3600,
                    days_spread=5,
                    return_visits=6,
                    certificate_uploaded=True,
                ),
                DemoPreloanAction(
                    title="Resume Review",
                    action_type="resume_improvement",
                    total_active_seconds=int(1.2 * 3600),
                    days_spread=2,
                    return_visits=2,
                    certificate_uploaded=False,
                ),
            ],
            dashboard_actions=[
                DemoDashboardAction(
                    action_id="action-aravind-1",
                    action_type="networking_outreach",
                    title="Australian Industry Networking",
                    rationale="Networking in Australia is critical for international graduates.",
                    assigned_at=MOCK_SNAPSHOT_TS,
                    expected_effort_hours=5,
                    total_active_seconds=0,
                    return_visits=0,
                    certificate_uploaded=False,
                    status="assigned",
                    readiness_score_delta=3,
                ),
            ],
        )

        self.students["student-sarah"] = DemoStudentState(
            student_id="student-sarah",
            full_name="Sarah Jenkins",
            destination_country="United Kingdom",
            program_family="business",
            macro_summary="UK financial services demand is MODERATE. Strong alumni connections are advantageous.",
            readiness_base_score=71,
            preloan_actions=[
                DemoPreloanAction(
                    title="Financial Analysis Prep",
                    action_type="skill_certification",
                    total_active_seconds=20 * 3600,
                    days_spread=12,
                    return_visits=15,
                    certificate_uploaded=True,
                ),
            ],
            dashboard_actions=[
                DemoDashboardAction(
                    action_id="action-sarah-1",
                    action_type="mock_interview",
                    title="Investment Banking Mock Interview",
                    rationale="High-stakes interviews require specialized preparation.",
                    assigned_at=MOCK_SNAPSHOT_TS,
                    expected_effort_hours=3,
                    total_active_seconds=0,
                    return_visits=0,
                    certificate_uploaded=False,
                    status="assigned",
                    readiness_score_delta=4,
                ),
            ],
        )

        self.cohorts["cohort-us-cs"] = DemoCohortState(
            cohort_id="cohort-us-cs",
            program_name="MS Computer Science",
            destination_country="United States",
            cohort_size=43,
            baseline_score=72,
            current_score=68,
        )
        self.cohorts["cohort-ca-ds"] = DemoCohortState(
            cohort_id="cohort-ca-ds",
            program_name="MS Data Science",
            destination_country="Canada",
            cohort_size=31,
            baseline_score=70,
            current_score=70,
        )
        self.cohorts["cohort-uk-business"] = DemoCohortState(
            cohort_id="cohort-uk-business",
            program_name="MBA",
            destination_country="United Kingdom",
            cohort_size=28,
            baseline_score=66,
            current_score=58,
        )

        self.cohort_alerts["alert-amber-1"] = DemoCohortAlert(
            alert_id="alert-amber-1",
            cohort_id="cohort-us-cs",
            severity="AMBER",
            delta=-4.0,
            primary_macro_driver="US tech hiring momentum softened.",
            recommended_action="Rule-based: review employability support actions for this cohort.",
            macro_snapshot_ts=MOCK_SNAPSHOT_TS,
            created_at=MOCK_SNAPSHOT_TS,
        )
        self.cohort_alerts["alert-red-1"] = DemoCohortAlert(
            alert_id="alert-red-1",
            cohort_id="cohort-uk-business",
            severity="RED",
            delta=-8.0,
            primary_macro_driver="UK hiring demand weakened materially for this cohort mix.",
            recommended_action="Rule-based: initiate proactive outreach and portfolio review.",
            macro_snapshot_ts=MOCK_SNAPSHOT_TS,
            created_at=MOCK_SNAPSHOT_TS,
        )

    def get_student(self, student_id: str) -> DemoStudentState | None:
        return self.students.get(student_id)

    def save_application(
        self,
        application_id: str,
        student_id: str | None,
        payload: OriginationScoringRequest,
        response: ScoringResponse,
        scored_at: str,
    ) -> None:
        self.applications[application_id] = DemoApplicationState(
            application_id=application_id,
            student_id=student_id,
            payload=payload,
            response=response,
            scored_at=scored_at,
        )
        if student_id:
            self.student_to_application_ids.setdefault(student_id, set()).add(application_id)

    def get_application(self, application_id: str) -> DemoApplicationState | None:
        return self.applications.get(application_id)

    def get_application_ids_for_student(self, student_id: str) -> list[str]:
        return sorted(self.student_to_application_ids.get(student_id, set()))

    def mark_dashboard_action_completed(
        self, student_id: str, action_id: str
    ) -> DashboardActionCompletionResult:
        student = self.get_student(student_id)
        if student is None:
            return DashboardActionCompletionResult(
                student_found=False,
                action_found=False,
                changed=False,
                action=None,
            )

        for action in student.dashboard_actions:
            if action.action_id == action_id:
                changed = False
                if action.status != "completed":
                    action.status = "completed"
                    action.completed_at = MOCK_ACTION_COMPLETION_TS
                    action.total_active_seconds = max(action.total_active_seconds, int(action.expected_effort_hours * 2400))
                    action.return_visits = max(action.return_visits, 2)
                    action.certificate_uploaded = action.action_type == "skill_certification"
                    changed = True
                return DashboardActionCompletionResult(
                    student_found=True,
                    action_found=True,
                    changed=changed,
                    action=action,
                )
        return DashboardActionCompletionResult(
            student_found=True,
            action_found=False,
            changed=False,
            action=None,
        )

    def get_dashboard_completed_actions(self, student_id: str) -> list[DemoDashboardAction]:
        student = self.get_student(student_id)
        if student is None:
            return []
        return [action for action in student.dashboard_actions if action.status == "completed"]

    def get_dashboard_pending_actions(self, student_id: str) -> list[DemoDashboardAction]:
        student = self.get_student(student_id)
        if student is None:
            return []
        return [action for action in student.dashboard_actions if action.status != "completed"]

    def get_readiness_score(self, student_id: str) -> int:
        student = self.get_student(student_id)
        if student is None:
            return 67

        delta = sum(
            action.readiness_score_delta
            for action in student.dashboard_actions
            if action.status == "completed"
        )
        return min(student.readiness_base_score + delta, 100)

    def get_behavioral_engagement(self, student_id: str) -> BehavioralEngagement:
        if self.get_tenacity_score(student_id) >= 0.75:
            return BehavioralEngagement.HIGH
        if self.get_tenacity_score(student_id) >= 0.45:
            return BehavioralEngagement.MODERATE
        return BehavioralEngagement.NONE

    def get_tenacity_score(self, student_id: str) -> float:
        student = self.get_student(student_id)
        if student is None:
            return 0.0
        completed_dashboard = len(self.get_dashboard_completed_actions(student_id))
        return min(0.79 + (completed_dashboard * 0.03), 1.0)

    def get_score_delta_points(self, student_id: str) -> int:
        return sum(
            3 if action.action_type == "skill_certification" else 2
            for action in self.get_dashboard_completed_actions(student_id)
        )

    def trigger_portfolio_rescore(self) -> None:
        if self.portfolio_rescore_triggered:
            return

        self.portfolio_rescore_triggered = True
        cohort = self.cohorts["cohort-ca-ds"]
        cohort.current_score = 66
        self.cohort_alerts["alert-amber-2"] = DemoCohortAlert(
            alert_id="alert-amber-2",
            cohort_id="cohort-ca-ds",
            severity="AMBER",
            delta=-4.0,
            primary_macro_driver="Canada hiring sentiment softened for data roles.",
            recommended_action="Rule-based: review placement action plans for the cohort.",
            macro_snapshot_ts=MOCK_ACTION_COMPLETION_TS,
            created_at=MOCK_ACTION_COMPLETION_TS,
        )

    def set_latest_event(
        self, application_id: str, event: SSEStudentProfileUpdatedEvent
    ) -> None:
        self.latest_events[application_id] = event

    def get_latest_event(
        self, application_id: str
    ) -> SSEStudentProfileUpdatedEvent | None:
        return self.latest_events.get(application_id)

    def get_latest_score_snapshot(self, application_id: str) -> tuple[int, Tier, float | None, BehavioralEngagement, str] | None:
        application = self.get_application(application_id)
        if application is None:
            return None
        return (
            application.response.repayment_score.score,
            application.response.repayment_score.tier,
            application.response.reliability.tenacity_score,
            application.response.reliability.behavioral_engagement,
            application.scored_at,
        )

    def sync_from_persistence(
        self,
        students: list[dict],
        cohorts: list[dict],
        alerts: list[dict],
        actions_by_student: dict[str, list[dict]],
    ) -> None:
        """
        Synchronize the in-memory store with database records.
        """
        # Load students
        for s in students:
            sid = s["id"]
            # Preserve existing demo metadata (summary/score) if already in memory
            existing = self.students.get(sid)
            self.students[sid] = DemoStudentState(
                student_id=sid,
                full_name=s["full_name"],
                destination_country=s["destination_country"],
                program_family=s["program_family"] or (existing.program_family if existing else "general"),
                macro_summary=existing.macro_summary if existing else "Market data loaded from database.",
                readiness_base_score=existing.readiness_base_score if existing else 67,
                preloan_actions=existing.preloan_actions if existing else [],
                dashboard_actions=[
                    DemoDashboardAction(
                        action_id=a["id"],
                        action_type=a["action_type"],
                        title=a["title"],
                        rationale="Loaded from persistence.",
                        assigned_at=a["assigned_at"],
                        expected_effort_hours=a["expected_effort_hours"],
                        total_active_seconds=a["total_active_seconds"],
                        return_visits=a["return_visits"],
                        certificate_uploaded=a["certificate_uploaded"],
                        status=a["status"],
                        completed_at=a["completed_at"],
                        readiness_score_delta=3 if a["action_type"] == "skill_certification" else 2,
                    )
                    for a in actions_by_student.get(sid, [])
                ] or (existing.dashboard_actions if existing else [])
            )

        # Load cohorts
        for c in cohorts:
            self.cohorts[c["id"]] = DemoCohortState(
                cohort_id=c["id"],
                program_name=c["program_name"],
                destination_country=c["destination_country"],
                cohort_size=c["cohort_size"],
                baseline_score=c["baseline_score"],
                current_score=c["current_score"],
            )

        # Load alerts
        for a in alerts:
            self.cohort_alerts[a["id"]] = DemoCohortAlert(
                alert_id=a["id"],
                cohort_id=a["cohort_id"],
                severity=a["severity"],
                delta=a["delta"],
                primary_macro_driver=a["primary_macro_driver"],
                recommended_action=a["recommended_action"],
                macro_snapshot_ts=a["macro_snapshot_ts"],
                created_at=a["created_at"],
            )
