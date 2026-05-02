from app.schemas.portfolio import CohortAlert, CohortRow
from app.services.demo_store import DemoStore
from app.services.persistence import PersistenceService


class PortfolioMonitorService:
    def __init__(self, store: DemoStore, persistence: PersistenceService | None = None) -> None:
        self.store = store
        self.persistence = persistence

    async def trigger_demo_rescore(self) -> None:
        if self.store.portfolio_rescore_triggered:
            return

        self.store.trigger_portfolio_rescore()

        # Persist the update if service available
        if self.persistence:
            try:
                cohort = self.store.cohorts["cohort-ca-ds"]
                await self.persistence.upsert_cohort(
                    cohort.cohort_id, cohort.program_name,
                    cohort.destination_country, cohort.cohort_size,
                    cohort.baseline_score, cohort.current_score
                )
                alert = self.store.cohort_alerts["alert-amber-2"]
                await self.persistence.upsert_cohort_alert(
                    alert.alert_id, alert.cohort_id, alert.severity,
                    alert.delta, alert.primary_macro_driver,
                    alert.recommended_action, alert.macro_snapshot_ts,
                    alert.created_at
                )
            except Exception:
                pass  # Best-effort

    def get_cohorts(self) -> list[CohortRow]:
        latest_alert_by_cohort = self._get_latest_alerts_index()
        cohort_rows: list[CohortRow] = []

        for cohort in self.store.cohorts.values():
            alert = latest_alert_by_cohort.get(cohort.cohort_id)
            cohort_rows.append(
                CohortRow(
                    cohort_id=cohort.cohort_id,
                    program_name=cohort.program_name,
                    destination_country=cohort.destination_country,
                    cohort_size=cohort.cohort_size,
                    baseline_score=cohort.baseline_score,
                    current_score=cohort.current_score,
                    delta=round(cohort.current_score - cohort.baseline_score, 2),
                    severity=alert.severity if alert else None,
                    triggered_at=alert.created_at if alert else None,
                    primary_macro_driver=alert.primary_macro_driver if alert else None,
                )
            )
        return cohort_rows

    def get_alerts(self) -> list[CohortAlert]:
        return [
            CohortAlert(
                cohort_id=a.cohort_id,
                severity=a.severity,
                delta=a.delta,
                primary_macro_driver=a.primary_macro_driver,
                recommended_action=a.recommended_action,
                macro_snapshot_ts=a.macro_snapshot_ts,
                triggered_at=a.created_at,
            )
            for a in self.store.cohort_alerts.values()
        ]

    def get_stats(self) -> dict[str, int]:
        latest_alert_by_cohort = self._get_latest_alerts_index()
        amber_count = 0
        red_count = 0

        for cohort in self.store.cohorts.values():
            alert = latest_alert_by_cohort.get(cohort.cohort_id)
            severity = alert.severity if alert else None
            if severity == "AMBER":
                amber_count += 1
            elif severity == "RED":
                red_count += 1
        
        return {
            "total_active_cohorts": len(self.store.cohorts),
            "amber_count": amber_count,
            "red_count": red_count,
        }

    def _get_latest_alerts_index(self) -> dict:
        latest_alert_by_cohort: dict = {}
        for alert in self.store.cohort_alerts.values():
            existing = latest_alert_by_cohort.get(alert.cohort_id)
            if existing is None or alert.created_at >= existing.created_at:
                latest_alert_by_cohort[alert.cohort_id] = alert
        return latest_alert_by_cohort
