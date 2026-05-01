from fastapi import APIRouter, Request, Response, status

from app.schemas.portfolio import CohortAlert, CohortRow, PortfolioDashboardResponse
from app.services.portfolio_monitor import PortfolioMonitorService

router = APIRouter()


@router.get("/dashboard", response_model=PortfolioDashboardResponse)
async def get_portfolio_dashboard(request: Request) -> PortfolioDashboardResponse:
    store = request.app.state.demo_store

    # Build latest-alert index per cohort
    latest_alert_by_cohort: dict = {}
    for alert in store.cohort_alerts.values():
        existing = latest_alert_by_cohort.get(alert.cohort_id)
        if existing is None or alert.created_at >= existing.created_at:
            latest_alert_by_cohort[alert.cohort_id] = alert

    amber_count = 0
    red_count = 0
    cohort_rows: list[CohortRow] = []

    for cohort in store.cohorts.values():
        alert = latest_alert_by_cohort.get(cohort.cohort_id)
        severity = alert.severity if alert else None
        if severity == "AMBER":
            amber_count += 1
        elif severity == "RED":
            red_count += 1
        cohort_rows.append(
            CohortRow(
                cohort_id=cohort.cohort_id,
                program_name=cohort.program_name,
                destination_country=cohort.destination_country,
                cohort_size=cohort.cohort_size,
                baseline_score=cohort.baseline_score,
                current_score=cohort.current_score,
                delta=round(cohort.current_score - cohort.baseline_score, 2),
                severity=severity,
                triggered_at=alert.created_at if alert else None,
                primary_macro_driver=alert.primary_macro_driver if alert else None,
            )
        )

    alerts = [
        CohortAlert(
            cohort_id=a.cohort_id,
            severity=a.severity,
            delta=a.delta,
            primary_macro_driver=a.primary_macro_driver,
            recommended_action=a.recommended_action,
            macro_snapshot_ts=a.macro_snapshot_ts,
            triggered_at=a.created_at,
        )
        for a in store.cohort_alerts.values()
    ]

    return PortfolioDashboardResponse(
        total_active_cohorts=len(store.cohorts),
        amber_count=amber_count,
        red_count=red_count,
        cohorts=cohort_rows,
        latest_alerts=alerts,
    )


@router.post("/rescore", status_code=status.HTTP_202_ACCEPTED)
async def trigger_portfolio_rescore(request: Request) -> Response:
    PortfolioMonitorService(request.app.state.demo_store).trigger_demo_rescore()
    return Response(status_code=status.HTTP_202_ACCEPTED)
