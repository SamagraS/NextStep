"""
Full backend audit script — covers all 11 check areas.
"""
import sys, json, time, os, asyncio, sqlite3
sys.path.insert(0, 'backend')

from pathlib import Path

RESULTS = []

def check(label, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append((label, status, detail))
    print(f"[{status}] {label}" + (f"  =>  {detail}" if detail else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ─────────────────────────────────────────────
# 1. IMPORTS + APP STARTUP
# ─────────────────────────────────────────────
section("1. APP STARTUP + ARTIFACTS")
try:
    from app.main import create_app
    from fastapi.testclient import TestClient
    from app.services.artifact_loader import ArtifactRegistry, ARTIFACT_CONTRACTS
    from app.core.config import get_settings

    app = create_app()
    settings = get_settings()
    check("App imports cleanly", True)
    check("Settings loaded", bool(settings.api_v1_prefix))
except Exception as e:
    check("App imports", False, str(e))
    sys.exit(1)

# Artifact contracts defined
check("Artifact contracts defined", len(ARTIFACT_CONTRACTS) >= 5, f"{len(ARTIFACT_CONTRACTS)} contracts")

# Check which PKL files actually exist
artifacts_dir = Path("artifacts")
artifact_names = [c.name for c in ARTIFACT_CONTRACTS]
existing_pkls = {c.name: (artifacts_dir / c.filename).exists() for c in ARTIFACT_CONTRACTS}
for name, exists in existing_pkls.items():
    check(f"Artifact on disk: {name}", exists)

# Load registry
registry = ArtifactRegistry(artifacts_dir)
registry.load()
ml_models_loaded = all([
    registry.get("salary_model_q15") is not None,
    registry.get("salary_model_q50") is not None,
    registry.get("salary_model_q85") is not None,
])
check("ML models loaded from disk", ml_models_loaded,
      "FALLBACK MODE ACTIVE" if not ml_models_loaded else "XGBoost inference active")
check("Encoding dicts loaded", registry.get("state_encode") is not None and registry.get("family_encode") is not None)

# ─────────────────────────────────────────────
# 2. API CONTRACT
# ─────────────────────────────────────────────
section("2. API CONTRACT + ENDPOINTS")

REQUIRED_ENDPOINTS = [
    ("POST", "/api/v1/score/origination"),
    ("GET",  "/api/v1/score/{application_id}/latest"),
    ("GET",  "/api/v1/score/{application_id}/stream"),
    ("POST", "/api/v1/student/action/complete"),
    ("GET",  "/api/v1/student/dashboard/{student_id}"),
    ("GET",  "/api/v1/portfolio/dashboard"),
    ("POST", "/api/v1/portfolio/rescore"),
    ("GET",  "/health"),
]

registered = {(list(r.methods)[0], r.path) for r in app.routes if hasattr(r, 'methods')}
for method, path in REQUIRED_ENDPOINTS:
    found = any(p == path and method in methods for methods, p in [(r.methods, r.path) for r in app.routes if hasattr(r, 'methods')])
    check(f"Endpoint {method} {path}", found)

with TestClient(app) as client:
    section("3. SCHEMA VALIDATION (422 on bad input)")
    # Bad payload - should 422
    r = client.post("/api/v1/score/origination", json={})
    check("Empty payload → 422", r.status_code == 422, f"got {r.status_code}")

    # present flag mismatch - should 422
    bad = {"full_name":"A","university_name":"MIT","program_name":"CS","destination_country":"US",
           "target_sector":"Tech","cgpa":8.0,"cgpa_present":False,"loan_amount_inr":1000000,
           "interest_rate_annual_pct":10,"repayment_term_months":84,"moratorium_months":9}
    r = client.post("/api/v1/score/origination", json=bad)
    check("Present flag mismatch → 422", r.status_code == 422, f"got {r.status_code}")

    # Valid Priya payload
    section("4. FULL DEMO FLOW")
    priya = {
        "student_id": "student-priya",
        "full_name": "Priya Sharma",
        "university_name": "University of Texas at Austin",
        "program_name": "MS Computer Science",
        "destination_country": "United States",
        "target_sector": "Cloud Engineering",
        "cgpa": 8.6, "cgpa_present": True,
        "internship_count": 2, "internship_count_present": True,
        "stem_opt_eligible": True, "stem_opt_eligible_present": True,
        "loan_amount_inr": 4500000,
        "interest_rate_annual_pct": 11.5,
        "repayment_term_months": 84,
        "moratorium_months": 9
    }
    t0 = time.time()
    r = client.post("/api/v1/score/origination", json=priya)
    latency_ms = (time.time() - t0) * 1000
    check("Origination request succeeds", r.status_code == 200, f"got {r.status_code}")
    check(f"Latency < 200ms", latency_ms < 200, f"{latency_ms:.1f}ms")

    if r.status_code == 200:
        d = r.json()
        app_id = d["application_id"]

        # Check all top-level response fields
        required_fields = ["application_id","placement_probability","delayed_placement_risk",
                           "salary_forecast","repayment_score","reliability",
                           "next_best_action","employer_match_list","explanation","model_metadata"]
        for f in required_fields:
            check(f"Response field: {f}", f in d)

        # Scoring checks
        score = d["repayment_score"]["score"]
        tier = d["repayment_score"]["tier"]
        check("Score is int 0-100", isinstance(score, int) and 0 <= score <= 100, f"score={score}")
        check("Tier is valid enum", tier in ["GREEN","AMBER","RED"], f"tier={tier}")
        check("Score == 71 (deterministic)", score == 71, f"got {score}")

        # L1 monotonic check
        pp = d["placement_probability"]
        check("L1 monotonic: p3 ≤ p6 ≤ p12", pp["p_3mo"] <= pp["p_6mo"] <= pp["p_12mo"],
              f"p3={pp['p_3mo']:.2f} p6={pp['p_6mo']:.2f} p12={pp['p_12mo']:.2f}")

        # L2 salary check
        sf = d["salary_forecast"]
        check("L2 method correct (US)", sf["method"] == "xgboost_quantile_regression_us")
        check("L2 q15 ≤ q50 ≤ q85", sf["pessimistic"] <= sf["realistic"] <= sf["optimistic"],
              f"q15={sf['pessimistic']} q50={sf['realistic']} q85={sf['optimistic']}")
        check("L2 salary realistic == 91000 (deterministic)", sf["realistic"] == 91000.0, f"got {sf['realistic']}")
        check("L2 EMI pct present", "emi_as_pct_realistic" in sf)

        # Behavioral boost check
        rs = d["repayment_score"]
        check("Behavioral base score present", rs.get("base_score_without_behavioral") is not None, f"base={rs.get('base_score_without_behavioral')}")
        check("Behavioral boost points present", rs.get("behavioral_boost_points") is not None, f"boost={rs.get('behavioral_boost_points')}")
        check("Boost == 3", rs.get("behavioral_boost_points") == 3, f"got {rs.get('behavioral_boost_points')}")
        check("Base without behavioral == 68", rs.get("base_score_without_behavioral") == 68, f"got {rs.get('base_score_without_behavioral')}")

        # Tenacity
        rel = d["reliability"]
        check("Tenacity score present", rel.get("tenacity_score") is not None, f"tenacity={rel.get('tenacity_score')}")
        check("Tenacity == 0.79", abs((rel.get("tenacity_score") or 0) - 0.79) < 0.01, f"got {rel.get('tenacity_score')}")

        # L4 bandit
        nba = d["next_best_action"]
        check("L4 returns 3 actions", len(nba) == 3, f"got {len(nba)}")
        check("L4 ranks are 1,2,3", [x["rank"] for x in nba] == [1,2,3])

        # Explanation
        exp = d["explanation"]
        check("Explanation tier_1 non-empty", bool(exp.get("tier_1")))
        check("Waterfall base_rate present", "base_rate" in exp.get("tier_2_attribution", {}))

        # Employer matches
        check("Employer matches returned", len(d.get("employer_match_list", [])) > 0)

        # Student dashboard
        section("5. STUDENT DASHBOARD")
        r2 = client.get("/api/v1/student/dashboard/student-priya")
        check("Dashboard 200", r2.status_code == 200, f"got {r2.status_code}")
        if r2.status_code == 200:
            dash = r2.json()
            check("Readiness score present", "readiness_score" in dash, f"score={dash.get('readiness_score')}")
            check("Readiness == 67", dash.get("readiness_score") == 67.0, f"got {dash.get('readiness_score')}")
            check("Pending actions returned", len(dash.get("pending_actions", [])) == 3)
            check("Completed actions returned", len(dash.get("completed_actions", [])) >= 0)

        # Unknown student → 404
        r3 = client.get("/api/v1/student/dashboard/unknown-xyz")
        check("Unknown student → 404", r3.status_code == 404, f"got {r3.status_code}")

        # Action completion
        section("6. ACTION COMPLETION + RECOMPUTE")
        score_before = score
        r4 = client.post("/api/v1/student/action/complete",
                         json={"student_id":"student-priya","action_id":"action-assign-1","bandit_arm_index":0})
        check("Action complete → 204", r4.status_code == 204, f"got {r4.status_code}")

        r5 = client.get(f"/api/v1/score/{app_id}/latest")
        check("Latest score 200", r5.status_code == 200, f"got {r5.status_code}")
        if r5.status_code == 200:
            new_score = r5.json()["score"]
            check("Score increased after action", new_score > score_before, f"{score_before} → {new_score}")
            check("New score == 74", new_score == 74, f"got {new_score}")

        # Portfolio
        section("7. PORTFOLIO DASHBOARD + RESCORE")
        rp = client.get("/api/v1/portfolio/dashboard")
        check("Portfolio dashboard 200", rp.status_code == 200, f"got {rp.status_code}")
        if rp.status_code == 200:
            pd = rp.json()
            check("3 cohorts returned", pd["total_active_cohorts"] == 3, f"got {pd['total_active_cohorts']}")
            check("Alerts returned", len(pd.get("latest_alerts",[])) >= 2)

        rr = client.post("/api/v1/portfolio/rescore")
        check("Portfolio rescore → 202", rr.status_code == 202, f"got {rr.status_code}")

    # ─────────────────────────────────────────────
    # Edge cases
    section("8. EDGE CASES")
    # Non-US destination
    non_us = {**priya, "student_id":None, "destination_country":"United Kingdom",
              "stem_opt_eligible":None, "stem_opt_eligible_present":False}
    r_uk = client.post("/api/v1/score/origination", json=non_us)
    check("Non-US scoring succeeds", r_uk.status_code == 200, f"got {r_uk.status_code}")
    if r_uk.status_code == 200:
        uk_d = r_uk.json()
        check("Non-US uses lookup method", uk_d["salary_forecast"]["method"] == "percentile_band_lookup",
              f"got {uk_d['salary_forecast']['method']}")
        uk_sf = uk_d["salary_forecast"]
        check("Non-US q15 ≤ q50 ≤ q85", uk_sf["pessimistic"] <= uk_sf["realistic"] <= uk_sf["optimistic"])
        check("No tenacity for anonymous", uk_d["reliability"]["tenacity_score"] is None)

    # Unknown university
    unk_uni = {**priya, "student_id":None, "university_name":"Zyx Unknown University 99999"}
    r_unk = client.post("/api/v1/score/origination", json=unk_uni)
    check("Unknown university doesn't crash", r_unk.status_code == 200, f"got {r_unk.status_code}")

    # Missing optional fields
    minimal = {**priya, "student_id":None, "cgpa":None, "cgpa_present":False,
               "internship_count":None, "internship_count_present":False,
               "stem_opt_eligible":None, "stem_opt_eligible_present":False}
    r_min = client.post("/api/v1/score/origination", json=minimal)
    check("All optionals missing doesn't crash", r_min.status_code == 200, f"got {r_min.status_code}")
    if r_min.status_code == 200:
        mflags = r_min.json()["reliability"]["imputation_flags"]
        check("Imputation flags populated", len(mflags) >= 2, f"flags={mflags}")

    # Extreme values
    extreme = {**priya, "student_id":None, "loan_amount_inr":999999999,
               "interest_rate_annual_pct":99, "repayment_term_months":600}
    r_ext = client.post("/api/v1/score/origination", json=extreme)
    check("Extreme values don't crash", r_ext.status_code == 200, f"got {r_ext.status_code}")

# ─────────────────────────────────────────────
# DB Persistence
section("9. DATABASE PERSISTENCE")
import time; time.sleep(0.5)
try:
    conn = sqlite3.connect("backend/nextstep.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    required_tables = {"users","students","applications","scoring_results","student_actions",
                       "cohort_alerts","cohorts","student_interaction_events","macro_signal_cache","bandit_checkpoints"}
    for t in required_tables:
        check(f"Table exists: {t}", t in tables)
    cur.execute("SELECT count(*) FROM applications")
    check("Applications written to DB", cur.fetchone()[0] > 0)
    cur.execute("SELECT count(*) FROM scoring_results")
    check("Scoring results written to DB", cur.fetchone()[0] > 0)
    cur.execute("SELECT count(*) FROM student_actions WHERE status='completed'")
    check("Completed action persisted", cur.fetchone()[0] > 0)
    conn.close()
except Exception as e:
    check("Database access", False, str(e))

# ─────────────────────────────────────────────
# Data Files
section("10. DATA + ARTIFACT FILES")
data_files = {
    "placement_lookup.csv": Path("data/processed/placement_lookup.csv"),
    "salary_band_factors.pkl": Path("artifacts/salary_band_factors.pkl"),
    "aggregate_outcomes.pkl": Path("artifacts/aggregate_outcomes.pkl"),
    "taxonomy_map.pkl": Path("artifacts/taxonomy_map.pkl"),
    "university_lookup.pkl": Path("artifacts/university_lookup.pkl"),
    "Colab training script": Path("data/colab_salary_model_training.py"),
}
for name, path in data_files.items():
    check(f"Data file exists: {name}", path.exists(), str(path))

# ─────────────────────────────────────────────
# SUMMARY
section("FINAL SUMMARY")
passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
failed = sum(1 for _, s, _ in RESULTS if s == "FAIL")
total = len(RESULTS)
print(f"\nTotal: {total} checks  |  PASS: {passed}  |  FAIL: {failed}")
print()
if failed:
    print("FAILURES:")
    for label, status, detail in RESULTS:
        if status == "FAIL":
            print(f"  ✗ {label}  →  {detail}")
else:
    print("ALL CHECKS PASSED")
