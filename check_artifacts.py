import sys
sys.path.insert(0, 'backend')
from pathlib import Path
from app.core.config import get_settings
from app.services.artifact_loader import ArtifactRegistry
from app.services.salary_model_service import SalaryModelService

settings = get_settings()
print("artifacts_dir from settings:", settings.artifacts_dir)
print("artifacts_dir resolved:", Path(settings.artifacts_dir).resolve())
print("backend/artifacts exists:", Path("backend/artifacts").exists())
print()

registry = ArtifactRegistry(settings.artifacts_dir)
registry.load()

for name in ['salary_model_q15','salary_model_q50','salary_model_q85','state_encode','family_encode']:
    obj = registry.get(name)
    status = type(obj).__name__ if obj is not None else "NOT LOADED"
    print(f"{name}: {status}")

print()
svc = SalaryModelService(registry)
print("ML available:", svc.available)
if svc.available:
    result = svc.predict('computer_science', 2)
    print("ML prediction (CS tier-2):", result)
    result2 = svc.predict('data_science', 1)
    print("ML prediction (DS tier-1):", result2)
else:
    print("FALLBACK MODE - models not loaded")
