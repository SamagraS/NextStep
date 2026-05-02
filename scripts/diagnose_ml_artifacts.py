import sys
from pathlib import Path
import joblib

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.append(str(BACKEND_DIR))

from app.services.artifact_loader import ARTIFACT_CONTRACTS
from app.services.salary_model_service import SalaryModelService

def test_existing_artifacts():
    print("Testing Existing ML Artifacts...")
    artifacts_dir = BACKEND_DIR / "artifacts"
    
    ml_artifacts = ["salary_model_q15", "salary_model_q50", "salary_model_q85", "state_encode", "family_encode"]
    
    loaded_artifacts = {}
    
    for name in ml_artifacts:
        contract = next(c for c in ARTIFACT_CONTRACTS if c.name == name)
        path = artifacts_dir / contract.filename
        print(f"\nLoading {name} from {path}...")
        if not path.exists():
            print(f"  FAILED: File does not exist.")
            continue
            
        try:
            obj = joblib.load(path)
            print(f"  SUCCESS: Loaded {type(obj).__name__}")
            loaded_artifacts[name] = obj
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")

    # Test Prediction if loaded
    if all(name in loaded_artifacts for name in ["salary_model_q15", "salary_model_q50", "salary_model_q85"]):
        print("\nTesting SalaryModelService.predict()...")
        sms = SalaryModelService(artifacts=loaded_artifacts)
        res = sms.predict(program_family="computer_science", institution_tier=1)
        if res:
            print(f"  Prediction SUCCESS: {res}")
        else:
            print("  Prediction FAILED (returned None or errored)")
    else:
        print("\nSkipping prediction test due to missing/failed artifacts.")

if __name__ == "__main__":
    test_existing_artifacts()
