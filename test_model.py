import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, 'backend')

from app.core.config import Settings
from app.services.artifact_loader import ArtifactRegistry
from app.services.salary_model_service import SalaryModelService
import xgboost as xgb
import numpy as np

s = Settings()
reg = ArtifactRegistry(s.artifacts_dir)
reg.load()

print("=== ARTIFACT LOAD STATUS ===")
for name in ['salary_model_q15','salary_model_q50','salary_model_q85','state_encode','family_encode']:
    obj = reg.get(name)
    status = type(obj).__name__ if obj is not None else "MISSING"
    print(f"  {name}: {status}")

svc = SalaryModelService(reg)
print(f"\nML available: {svc.available}")

if not svc.available:
    print("FAIL: ML not available")
    sys.exit(1)

print("\n=== PREDICTION TESTS ===")

state_encode = reg.get("state_encode")
family_encode = reg.get("family_encode")
print(f"family_encode: {family_encode}")
print(f"state_encode sample (CA, NY, TX): CA={state_encode.get('CA')}, NY={state_encode.get('NY')}, TX={state_encode.get('TX')}")

tests = [
    ("Priya — CS, CA, tier 2",   "computer_science", 2, "CA"),
    ("DS, NY, tier 1 (elite)",   "data_science",     1, "NY"),
    ("Business, TX, tier 3",     "business",         3, "TX"),
    ("General, FL, tier 4",      "general",          4, "FL"),
    ("CS, CA, tier 1 (elite)",   "computer_science", 1, "CA"),
    ("CS, CA, tier 4 (low)",     "computer_science", 4, "CA"),
]

all_pass = True
for label, family, tier, state in tests:
    result = svc.predict(family, tier, state)
    if result is None:
        print(f"  FALLBACK  {label} => None (model output below realism guard)")
        all_pass = False
    else:
        q15, q50, q85 = result
        mono_ok = q15 <= q50 <= q85
        realistic = 50_000 <= q50 <= 300_000
        status = "PASS" if mono_ok and realistic else "FAIL"
        if not (mono_ok and realistic):
            all_pass = False
        print(f"  [{status}] {label}")
        print(f"         q15=${q15:,.0f}  q50=${q50:,.0f}  q85=${q85:,.0f}  monotonic={mono_ok}  realistic={realistic}")

print("\n=== TIER GRADIENT CHECK (CS, CA) ===")
print("Tier 1 q50 should > Tier 2 q50 > Tier 3 q50 > Tier 4 q50")
tier_preds = []
for tier in [1, 2, 3, 4]:
    r = svc.predict("computer_science", tier, "CA")
    q50 = r[1] if r else None
    tier_preds.append(q50)
    print(f"  Tier {tier}: ${q50:,.0f}" if q50 else f"  Tier {tier}: FALLBACK")

gradient_ok = all(
    tier_preds[i] is not None and tier_preds[i+1] is not None and tier_preds[i] >= tier_preds[i+1]
    for i in range(3)
)
print(f"  Gradient correct (tier 1 >= 2 >= 3 >= 4): {gradient_ok}")
if not gradient_ok:
    all_pass = False

print("\n=== END-TO-END DEMO FLOW (Priya) ===")
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app()
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
with TestClient(app) as client:
    import time
    t0 = time.time()
    r = client.post("/api/v1/score/origination", json=priya)
    ms = (time.time() - t0) * 1000
    if r.status_code == 200:
        d = r.json()
        sf = d["salary_forecast"]
        rs = d["repayment_score"]
        print(f"  Status: 200 OK  ({ms:.1f}ms)")
        print(f"  L2 method: {sf['method']}")
        print(f"  Salary: q15=${sf['pessimistic']:,.0f}  q50=${sf['realistic']:,.0f}  q85=${sf['optimistic']:,.0f}")
        print(f"  Score: {rs['score']} ({rs['tier']})  boost={rs.get('behavioral_boost_points')}")
        l2_is_ml = sf['method'] == 'xgboost_quantile_regression_us'
        print(f"  ML inference active: {l2_is_ml}")
        if not l2_is_ml:
            print("  NOTE: Still using seeded fallback — realism guard triggered")
            all_pass = False
    else:
        print(f"  FAIL: {r.status_code}")
        all_pass = False

print(f"\n{'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
