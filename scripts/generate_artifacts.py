import os
import sys
from pathlib import Path
import joblib
import pandas as pd

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
DATA_DIR = REPO_ROOT / "data"
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"

# Add backend to sys.path to allow imports from 'app'
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

try:
    from app.outcomes.mapping import KEYWORD_TO_PROGRAM
except ImportError:
    # Fallback if app structure is not exactly as expected in the execution environment
    KEYWORD_TO_PROGRAM = {}

def ensure_artifacts_dir():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_aggregate_outcomes():
    print("Generating aggregate_outcomes.pkl...")
    source_path = DATA_DIR / "processed" / "placement_lookup.csv"
    if not source_path.exists():
        print(f"Warning: {source_path} missing. Skipping.")
        return

    df = pd.read_csv(source_path)
    outcomes = {}

    # We use Tier 2 as the representative baseline for non-US destinations 
    # to avoid double-counting tier adjustments in the service layer.
    for _, row in df.iterrows():
        country = str(row["country"]).lower()
        family = str(row["program_family"])
        tier = int(row["institution_tier"])
        
        # Heuristic: Pick Tier 2 if available, or first encountered for that country/family
        key_base = (country, family)
        
        for window, col in [("3mo", "p3"), ("6mo", "p6"), ("12mo", "p12")]:
            dict_key = (country, family, window)
            # If we already have a Tier 2 entry, don't overwrite it with Tier 3 etc.
            if dict_key in outcomes and tier != 2:
                continue
            outcomes[dict_key] = float(row[col])

    joblib.dump(outcomes, ARTIFACTS_DIR / "aggregate_outcomes.pkl")
    print(f"Saved {len(outcomes)} entries to aggregate_outcomes.pkl")

def generate_salary_band_factors():
    print("Generating salary_band_factors.pkl...")
    source_path = DATA_DIR / "processed" / "salary_lookup.csv"
    if not source_path.exists():
        print(f"Warning: {source_path} missing. Skipping.")
        return

    df = pd.read_csv(source_path)
    factors = {}

    for _, row in df.iterrows():
        country = str(row["country"]).lower()
        if country in {"united states", "usa", "us"}:
            continue
            
        family = str(row["program_family"])
        tier = int(row["institution_tier"])
        
        dict_key = (country, family)
        # Prefer Tier 2 as baseline for non-US
        if dict_key in factors and tier != 2:
            continue
            
        factors[dict_key] = {
            "pessimistic": float(row["p15"]),
            "realistic": float(row["p50"]),
            "optimistic": float(row["p85"])
        }

    joblib.dump(factors, ARTIFACTS_DIR / "salary_band_factors.pkl")
    print(f"Saved {len(factors)} entries to salary_band_factors.pkl")

def generate_taxonomy_map():
    print("Generating taxonomy_map.pkl...")
    
    # Discipline mapping as seen in reference_data.py
    FAMILY_TO_DISCIPLINE = {
        "computer_science": "engineering",
        "data_science": "engineering",
        "engineering": "engineering",
        "business": "business",
        "finance": "business",
        "economics": "business",
        "mathematics": "quantitative",
        "general_studies": "general"
    }

    taxonomy = {}
    # Deterministic sort and normalization of keys
    for keyword in sorted(KEYWORD_TO_PROGRAM.keys()):
        family = KEYWORD_TO_PROGRAM[keyword]
        clean_key = keyword.strip().lower()
        taxonomy[clean_key] = {
            "program_family": family,
            "discipline": FAMILY_TO_DISCIPLINE.get(family, "general")
        }

    joblib.dump(taxonomy, ARTIFACTS_DIR / "taxonomy_map.pkl")
    print(f"Saved {len(taxonomy)} entries to taxonomy_map.pkl")

def generate_university_lookup():
    print("Generating university_lookup.pkl...")
    
    # Consolidating from ingestion.py tier_map and reference_data.py fallbacks
    universities = {
        "University of Texas Austin": {
            "aliases": ("University of Texas at Austin", "UT Austin"),
            "institution_tier": 1
        },
        "University of Toronto": {
            "aliases": ("U of T",),
            "institution_tier": 1
        },
        "University of Melbourne": {
            "aliases": ("Melbourne University",),
            "institution_tier": 1
        },
        "Indian Institute of Technology Roorkee": {
            "aliases": ("IIT Roorkee", "IITR"),
            "institution_tier": 1
        },
        "International Institute of Information Technology Hyderabad": {
            "aliases": ("IIIT Hyderabad", "IIITH"),
            "institution_tier": 1
        },
        "University of Hyderabad": {
            "aliases": ("UoH",),
            "institution_tier": 2
        }
    }

    joblib.dump(universities, ARTIFACTS_DIR / "university_lookup.pkl")
    print(f"Saved {len(universities)} entries to university_lookup.pkl")

def verify_artifacts():
    print("\nVerifying artifacts via ArtifactRegistry...")
    try:
        from app.services.artifact_loader import ArtifactRegistry
        registry = ArtifactRegistry(ARTIFACTS_DIR)
        registry.load()
        
        health = registry.snapshot()
        missing = [a.name for a in health if not a.loaded]
        
        if missing:
            print(f"Warning: Some artifacts failed to load: {missing}")
        else:
            print("Success: All artifacts loaded correctly.")
            
        # Specific check for the 4 new artifacts
        new_artifacts = ["aggregate_outcomes", "salary_band_factors", "taxonomy_map", "university_lookup"]
        for name in new_artifacts:
            obj = registry.get(name)
            if obj is not None:
                print(f"  - {name}: {type(obj).__name__} (len={len(obj) if hasattr(obj, '__len__') else 'N/A'})")
            else:
                print(f"  - {name}: FAILED TO LOAD")
                
    except Exception as e:
        print(f"Verification failed with error: {e}")

if __name__ == "__main__":
    ensure_artifacts_dir()
    generate_aggregate_outcomes()
    generate_salary_band_factors()
    generate_taxonomy_map()
    generate_university_lookup()
    verify_artifacts()
    print("\nDone generating and verifying artifacts.")

