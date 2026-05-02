import sys
from pathlib import Path
import joblib

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.append(str(BACKEND_DIR))

from app.services.artifact_loader import ArtifactRegistry
from app.services.reference_data import ReferenceDataService
from app.services.layer1_placement import Layer1PlacementService
from app.services.layer2_salary import Layer2SalaryService
from app.models.feature_assembly import MacroSignalSnapshot, TaxonomyResolution, UniversityResolution, FeatureAssemblyResult
from app.schemas.score import OriginationScoringRequest

def test_integration():
    print("Initializing ArtifactRegistry...")
    artifacts_dir = BACKEND_DIR / "artifacts"
    registry = ArtifactRegistry(artifacts_dir)
    registry.load()

    # 1. Test University Lookup (ReferenceDataService)
    print("\nTesting University Lookup Integration...")
    ref_data = ReferenceDataService(artifacts=registry)
    
    # "IIIT Hyderabad" is in our PKL but NOT in the hardcoded fallback list
    res = ref_data.resolve_university("IIIT Hyderabad")
    print(f"  Target: IIIT Hyderabad")
    print(f"  Match Status: {res.match_status}")
    print(f"  Institution Tier: {res.institution_tier}")
    print(f"  Source: {res.source}")
    
    if res.institution_tier == 1 and res.source == "artifact_lookup":
        print("  SUCCESS: Picked up from artifact.")
    else:
        # Note: I need to check if reference_data.py actually sets source to "artifact_lookup"
        # Let's check the code again.
        pass

    # 2. Test Taxonomy Map (ReferenceDataService)
    print("\nTesting Taxonomy Map Integration...")
    # "artificial intelligence" is in KEYWORD_TO_PROGRAM
    tax_res = ref_data.map_program("Masters in Artificial Intelligence")
    print(f"  Target: Artificial Intelligence")
    print(f"  Program Family: {tax_res.program_family}")
    print(f"  Source: {tax_res.source}")
    
    if tax_res.source == "artifact_taxonomy_map":
        print("  SUCCESS: Picked up from artifact.")

    # 3. Test Placement Base Rate (Layer1PlacementService)
    print("\nTesting Placement Base Rate Integration...")
    l1 = Layer1PlacementService(artifacts=registry)
    
    # Create a mock assembled result
    mock_assembled = FeatureAssemblyResult(
        university=res,
        taxonomy=tax_res,
        macro=MacroSignalSnapshot(destination_country="Australia", market_risk_sub=0.5, summary="", macro_snapshot_ts="", source="", stale_signal_warning=None),
        tenacity=None,
        cgpa=None,
        internship_count=None,
        stem_opt_eligible=None,
        imputation_flags=[],
        feature_dict={
            "program_family": "computer_science",
            "institution_tier": 1,
            "moratorium_months": 6
        }
    )
    
    base_rate = l1._base_rate_anchor(mock_assembled, moratorium_months=6)
    print(f"  Target: Australia / Computer Science / 6mo")
    print(f"  Base Rate: {base_rate}")
    
    # Check if it matches artifact data (I know from generate_artifacts it should be there)
    # Australia, computer_science, Tier 2 in CSV was p6=0.6376. 
    # Since I used Tier 2 as baseline in pkl, it should be around 0.638.
    if base_rate != 0.5: # 0.5 is the hardcoded global fallback
        print("  SUCCESS: Picked up from artifact (non-default rate).")

    # 4. Test Salary Band (Layer2SalaryService)
    print("\nTesting Salary Band Integration...")
    l2 = Layer2SalaryService(artifacts=registry)
    
    # Non-US destination: Australia
    # In my generate_artifacts.py: 
    # Australia, computer_science, Tier 2: p15=58734, p50=75300, p85=96384
    p, r, o = l2._non_us_salary_values(
        destination="australia",
        program_family="computer_science",
        institution_tier=1
    )
    print(f"  Target: Australia / Computer Science / Tier 1")
    print(f"  Forecast: {p} / {r} / {o}")
    
    if r == 75300.0:
        print("  SUCCESS: Picked up from artifact.")

if __name__ == "__main__":
    try:
        test_integration()
    except Exception as e:
        print(f"\nIntegration test failed: {e}")
        import traceback
        traceback.print_exc()
