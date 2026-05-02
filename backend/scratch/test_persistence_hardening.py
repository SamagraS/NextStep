import asyncio
import os
import sys

# Add backend to sys.path to allow imports
sys.path.append(os.path.abspath("backend"))

from app.core.config import get_settings
from app.db.database import Database
from app.services.demo_store import DemoStore
from app.services.persistence import PersistenceService
from app.services.portfolio_monitor import PortfolioMonitorService

async def test_persistence_hardening():
    print("--- Starting Persistence Hardening Verification ---")
    settings = get_settings()
    database = Database(settings.database_url)
    await database.initialize()
    
    # PHASE 1: Initial Setup and Modification
    print("PHASE 1: Seeding and modifying state...")
    store = DemoStore()
    persistence = PersistenceService(database)
    
    # Seed
    await persistence.seed_all(store)
    
    # 1. Complete an action for Priya
    print("Completing action for Priya...")
    # Check current score
    initial_score = store.get_readiness_score("student-priya")
    print(f"Initial readiness score: {initial_score}")
    
    # Mark action completed in-memory
    store.mark_dashboard_action_completed("student-priya", "action-assign-1")
    action = [a for a in store.students["student-priya"].dashboard_actions if a.action_id == "action-assign-1"][0]
    
    # Persist it
    await persistence.upsert_student_action(
        action.action_id, "student-priya", action.action_type, action.title,
        action.status, action.assigned_at, action.expected_effort_hours,
        action.total_active_seconds, action.return_visits, action.certificate_uploaded,
        action.completed_at
    )
    
    new_score_in_memory = store.get_readiness_score("student-priya")
    print(f"Score after completion: {new_score_in_memory}")
    assert new_score_in_memory > initial_score
    
    # 2. Trigger Portfolio Rescore
    print("Triggering Portfolio Rescore...")
    monitor = PortfolioMonitorService(store, persistence=persistence)
    await monitor.trigger_demo_rescore()
    
    alerts_count = len(store.cohort_alerts)
    print(f"Alerts count in memory: {alerts_count}")
    assert alerts_count == 3
    
    # PHASE 2: Simulate Restart
    print("\nPHASE 2: Simulating restart and reloading from DB...")
    await database.close()
    
    # Re-open
    await database.initialize()
    new_store = DemoStore()
    new_persistence = PersistenceService(database)
    
    # Reload logic (similar to main.py)
    students_db = await new_persistence.get_all_students()
    cohorts_db = await new_persistence.get_all_cohorts()
    alerts_db = await new_persistence.get_all_alerts()
    actions_by_student = {}
    for s in students_db:
        actions_by_student[s["id"]] = await new_persistence.get_all_student_actions(s["id"])
    
    new_store.sync_from_persistence(students_db, cohorts_db, alerts_db, actions_by_student)
    
    # VERIFICATION
    print("Verifying persistence...")
    
    # Check Priya's score
    final_score = new_store.get_readiness_score("student-priya")
    print(f"Final readiness score after reload: {final_score}")
    assert final_score == new_score_in_memory
    
    # Check Alerts count
    final_alerts_count = len(new_store.cohort_alerts)
    print(f"Final alerts count after reload: {final_alerts_count}")
    assert final_alerts_count == 3
    
    # Check specific alert
    assert "alert-amber-2" in new_store.cohort_alerts
    
    await database.close()
    print("--- Persistence Hardening Verification Complete: ALL PASSED ---")

if __name__ == "__main__":
    asyncio.run(test_persistence_hardening())
