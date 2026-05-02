import asyncio
import os
import sys

# Add backend to sys.path to allow imports
sys.path.append(os.path.abspath("backend"))

from app.services.demo_store import DemoStore
from app.services.portfolio_monitor import PortfolioMonitorService

async def test_portfolio_refinement():
    print("--- Starting Portfolio Refinement Verification ---")
    store = DemoStore()
    service = PortfolioMonitorService(store)
    
    # 1. Test get_cohorts
    print("Testing get_cohorts...")
    cohorts = service.get_cohorts()
    assert len(cohorts) == 3
    assert cohorts[0].cohort_id == "cohort-us-cs"
    assert cohorts[0].severity == "AMBER"
    print("get_cohorts OK.")
    
    # 2. Test get_alerts
    print("Testing get_alerts...")
    alerts = service.get_alerts()
    assert len(alerts) == 2
    assert any(a.alert_id == "alert-amber-1" for a in store.cohort_alerts.values()) # Using store directly because get_alerts returns CohortAlert (no id in schema)
    print("get_alerts OK.")
    
    # 3. Test get_stats
    print("Testing get_stats...")
    stats = service.get_stats()
    assert stats["total_active_cohorts"] == 3
    assert stats["amber_count"] == 1
    assert stats["red_count"] == 1
    print("get_stats OK.")
    
    # 4. Test Rescore
    print("Testing trigger_demo_rescore...")
    service.trigger_demo_rescore()
    stats_after = service.get_stats()
    assert stats_after["amber_count"] == 2
    assert len(service.get_alerts()) == 3
    print("trigger_demo_rescore OK.")
    
    print("--- Portfolio Refinement Verification Complete: ALL PASSED ---")

if __name__ == "__main__":
    asyncio.run(test_portfolio_refinement())
