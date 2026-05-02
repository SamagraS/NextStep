import json
import os
import sys

# Add backend to sys.path to allow imports
sys.path.append(os.path.abspath("backend"))

from app.services.contract_examples import (
    build_placeholder_alert_list,
    build_placeholder_cohort_list,
    build_placeholder_login_response,
    build_placeholder_portfolio_dashboard,
    build_placeholder_scoring_response,
    build_placeholder_student_dashboard,
)
from app.schemas.score import OriginationScoringRequest

def test_contract_validity():
    print("--- Starting Contract Validity Verification ---")
    
    # 1. Auth Example
    print("Verifying Auth Example...")
    login_resp = build_placeholder_login_response()
    print(f"Auth Response: {login_resp.model_dump_json()[:50]}...")
    
    # 2. Portfolio Examples
    print("Verifying Portfolio Examples...")
    cohorts = build_placeholder_cohort_list()
    assert len(cohorts) > 0
    alerts = build_placeholder_alert_list()
    assert len(alerts) > 0
    dashboard = build_placeholder_portfolio_dashboard()
    assert dashboard.total_active_cohorts > 0
    
    # 3. Scoring Example (needs a payload)
    print("Verifying Scoring Example...")
    mock_payload = OriginationScoringRequest(
        full_name="Test User",
        university_name="Stanford",
        program_name="CS",
        destination_country="US",
        target_sector="Tech",
        loan_amount_inr=5000000,
        interest_rate_annual_pct=10.5,
        repayment_term_months=120,
        moratorium_months=6
    )
    scoring_resp = build_placeholder_scoring_response(mock_payload)
    assert scoring_resp.repayment_score.score == 71
    
    # 4. Student Dashboard Example
    print("Verifying Student Dashboard Example...")
    student_resp = build_placeholder_student_dashboard("student-priya")
    assert student_resp.readiness_score == 71
    
    print("--- Contract Validity Verification Complete: ALL PASSED ---")

if __name__ == "__main__":
    test_contract_validity()
