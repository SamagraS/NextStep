# ETL Pipeline Plan for NextStep Artifacts

This document outlines the design for the ETL pipeline required to generate the missing PKL artifacts in `backend/artifacts/`. The goal is to provide deterministic, demo-safe artifacts derived from existing repo data.

## Artifact Status Summary

| Artifact | Source File(s) | Status | Expected Structure |
| :--- | :--- | :--- | :--- |
| `aggregate_outcomes.pkl` | `data/processed/placement_lookup.csv` | **EXISTS** | `dict[(country, program, window), float]` |
| `salary_band_factors.pkl` | `data/processed/salary_lookup.csv` | **EXISTS** | `dict[(country, program), dict]` |
| `taxonomy_map.pkl` | `backend/app/outcomes/mapping.py` | **EXISTS** (Logic) | `dict[keyword, dict[family, discipline]]` |
| `university_lookup.pkl` | `backend/app/outcomes/ingestion.py`, `reference_data.py` | **PARTIAL** | `dict[canonical_name, dict]` |

---

## 1. `aggregate_outcomes.pkl`

### Design
- **Source**: `data/processed/placement_lookup.csv`
- **Logic**: For each row in the CSV, create three entries in the dictionary corresponding to the 3-month, 6-month, and 12-month placement horizons.
- **Key**: `tuple(country.lower(), program_family, window)` where `window` is one of `"3mo"`, `"6mo"`, `"12mo"`.
- **Value**: `float` (base rate).
- **Fallback Assumption**: If multiple tiers exist for a country/program, prioritize Tier 2 as the representative "average" for the base rate, as most international data in the repo is centered on Tier 2.
- **Output Path**: `backend/artifacts/aggregate_outcomes.pkl`

### Key Fields
- `country` -> `destination`
- `program_family` -> `program_family`
- `p3` -> `3mo`
- `p6` -> `6mo`
- `p12` -> `12mo`

---

## 2. `salary_band_factors.pkl`

### Design
- **Source**: `data/processed/salary_lookup.csv`
- **Logic**: Extract median and quantile salaries for non-US destinations.
- **Key**: `tuple(country.lower(), program_family)`
- **Value**: `dict` with keys `pessimistic` (from `p15`), `realistic` (from `p50`), and `optimistic` (from `p85`).
- **Fallback Assumption**: Use Tier 2 as the baseline for international lookups.
- **Output Path**: `backend/artifacts/salary_band_factors.pkl`

---

## 3. `taxonomy_map.pkl`

### Design
- **Source**: `backend/app/outcomes/mapping.py` (Specifically the `KEYWORD_TO_PROGRAM` dictionary).
- **Logic**: Convert the existing internal mapping into a serialized artifact.
- **Key**: `str` (keyword, e.g., "computing", "analytics").
- **Value**: `dict` containing `program_family` and `discipline`.
- **Note**: This artifact completes the `ReferenceDataService.map_program` logic by providing the lookup dictionary it expects.
- **Output Path**: `backend/artifacts/taxonomy_map.pkl`

---

## 4. `university_lookup.pkl`

### Design
- **Source**: 
  - `backend/app/outcomes/ingestion.py` (`tier_map` for India)
  - `backend/app/services/reference_data.py` (Hardcoded fallbacks)
- **Logic**: Aggregate known universities into a canonical lookup dictionary.
- **Key**: `str` (Canonical University Name).
- **Value**: `dict` with `aliases` (tuple) and `institution_tier` (int).
- **Demo-Safe Data**:
  - University of Texas Austin (Tier 1)
  - University of Toronto (Tier 1)
  - University of Melbourne (Tier 1)
  - IIT Roorkee (Tier 1)
  - IIIT Hyderabad (Tier 1)
  - University of Hyderabad (Tier 2)
- **Output Path**: `backend/artifacts/university_lookup.pkl`

---

## Next Steps
1. Create a script `scripts/generate_artifacts.py` implementing the above logic using `joblib`.
2. Run the script to populate `backend/artifacts/`.
3. Verify via `artifact_loader.py` health checks.
