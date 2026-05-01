# NextStep

NextStep is a FastAPI backend and outcomes forecasting pipeline for education and career planning. It combines raw public datasets, normalized mapping tables, and generated lookup artifacts to estimate placement probabilities, salary bands, and a macro-adjusted risk score for a student profile.

The repository is centered on two workflows:

- serving API endpoints for scoring, dashboards, and forecasting
- rebuilding the outcomes pipeline from raw data into processed lookup artifacts

Project documentation lives in [docs/architecture.md](docs/architecture.md), [docs/flow.md](docs/flow.md), and [docs/communication.md](docs/communication.md).

## What This Project Does

The backend exposes a small set of demo-oriented APIs and a separate outcomes prediction endpoint. Under the hood, the application loads artifact snapshots at startup, stores lightweight state in SQLite, and serves data through FastAPI.

The outcomes pipeline consumes raw data from sources such as HESA, QILT, Eurostat, OFLC H1B, NIRF, and World Bank. It transforms those inputs into processed lookup tables that the API uses for predictions.

## Repository Layout

```text
backend/
  app/
    main.py                 FastAPI application entrypoint
    api/                    API router and route modules
    core/                   Settings and application configuration
    db/                     SQLite database setup
    outcomes/               Data ingestion, preprocessing, mapping, and inference
    schemas/                Pydantic request and response schemas
    services/               API service layer and demo helpers
    utils/                  Shared utilities
  build_outcomes_pipeline.py Rebuilds generated outcomes artifacts
  demo_outcomes_example.py  Runs a sample forecast

data/
  raw/                      Source datasets checked into the repo
  mappings/                 Canonical mapping tables
  processed/                Generated lookup tables and demo outputs
```

## Key Features

- FastAPI service with health, scoring, student, portfolio, and outcomes routes
- SQLite-backed application state with startup initialization
- Outcomes prediction endpoint for placement, salary, and risk estimates
- Rebuildable data pipeline for reproducible processed artifacts
- Demo script and saved sample output for quick verification

## Requirements

The project uses Python and the packages listed in [requirements.txt](requirements.txt).

Major runtime dependencies include:

- FastAPI and Uvicorn for the API server
- Pandas, NumPy, and OpenPyXL for data processing
- Pdfplumber for extracting tables from PDFs
- XGBoost and Joblib for model-assisted inference paths

## Setup

### 1. Create and activate a virtual environment

If you already have a virtual environment in this workspace, activate it. On Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Confirm the data layout

The pipeline expects the repository data folders to be present as checked in:

- `data/raw/` for source inputs
- `data/mappings/` for canonical program-family mappings
- `data/processed/` for generated artifacts

The application also loads settings from `backend/.env` if that file exists.

## Configuration

Configuration lives in [backend/app/core/config.py](backend/app/core/config.py).

Settings are read from environment variables with the `NEXTSTEP_` prefix and default to these values:

- `NEXTSTEP_APP_NAME` -> `NextStep Backend`
- `NEXTSTEP_APP_VERSION` -> `0.1.0`
- `NEXTSTEP_API_V1_PREFIX` -> `/api/v1`
- `NEXTSTEP_DATABASE_URL` -> `backend/nextstep.db`
- `NEXTSTEP_ARTIFACTS_DIR` -> `artifacts`
- `NEXTSTEP_DATA_DIR` -> `data`
- `NEXTSTEP_PROCESSED_DATA_DIR` -> `data/processed`
- `NEXTSTEP_MAPPINGS_DIR` -> `data/mappings`

You can override any of those in your environment or in `backend/.env`.

Example:

```env
NEXTSTEP_DATABASE_URL=backend/nextstep.db
NEXTSTEP_ARTIFACTS_DIR=artifacts
NEXTSTEP_DATA_DIR=data
NEXTSTEP_PROCESSED_DATA_DIR=data/processed
NEXTSTEP_MAPPINGS_DIR=data/mappings
```

## Running The API

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='backend'
python -m uvicorn app.main:app --reload
```

This starts the FastAPI app defined in [backend/app/main.py](backend/app/main.py).

Once the server is running, open:

- `http://127.0.0.1:8000/docs` for the interactive Swagger UI
- `http://127.0.0.1:8000/redoc` for the ReDoc view
- `http://127.0.0.1:8000/health` for the top-level health check

## API Surface

The API router is assembled in [backend/app/api/router.py](backend/app/api/router.py) and mounted under `/api/v1`.

### Health

- `GET /health`
- `GET /api/v1/health`

Returns the application status, database state, and artifact snapshot.

### Outcomes

- `POST /api/v1/outcomes/predict`

Example payload:

```json
{
  "program_family": "computer science",
  "destination_country": "United States",
  "institution_tier": 1
}
```

The response includes:

- student context
- placement probabilities for 3, 6, and 12 months
- salary band estimates
- risk score and label
- data sources used
- explanatory notes

### Score

- `POST /api/v1/score/origination`
- `GET /api/v1/score/{application_id}/latest`
- `GET /api/v1/score/{application_id}/stream`

These endpoints drive the demo scoring flow, including latest-score lookup and a server-sent events stream.

### Student

- `GET /api/v1/student/dashboard/{student_id}`
- `POST /api/v1/student/action/complete`

These endpoints support the student dashboard and action-completion flow.

### Portfolio

- `POST /api/v1/portfolio/rescore`

Triggers a demo portfolio rescore.

## Outcomes Pipeline

The outcomes pipeline is implemented under [backend/app/outcomes](backend/app/outcomes).

High-level stages:

1. Ingestion reads the supported raw datasets from `data/raw/`.
2. Preprocessing standardizes the source data into placement, salary, macro, and microdata tables.
3. Mapping normalizes program and taxonomy labels into the canonical program-family set.
4. Model builders materialize lookup tables for placement, salary, and macro factors.
5. Inference loads the processed artifacts and produces the final forecast response.

### Rebuild Processed Artifacts

To rebuild all generated outcomes artifacts:

```powershell
$env:PYTHONPATH='backend'
python backend/build_outcomes_pipeline.py
```

This regenerates the processed lookup files in `data/processed/`.

### Demo Prediction

To run the example forecast script:

```powershell
$env:PYTHONPATH='backend'
python backend/demo_outcomes_example.py
```

A saved example output is checked in at `data/processed/example_prediction_us.json`.

## Data Sources

The current pipeline is wired to these source families:

- HESA
- QILT
- Eurostat
- OFLC H1B
- NIRF
- World Bank

### Raw Data

The repository keeps the raw source inputs under `data/raw/` so the processed artifacts can be rebuilt locally.

Important raw folders include:

- `data/raw/hesa/`
- `data/raw/qilt/`
- `data/raw/eurostat/`
- `data/raw/oflc/`
- `data/raw/nirf/`
- `data/raw/world_bank/`

### Processed Outputs

Generated artifacts are written to `data/processed/` and include:

- `placement_lookup.csv`
- `salary_lookup.csv`
- `macro_lookup.csv`
- `source_manifest.json`
- `example_prediction_us.json`

## Development Notes

- The application uses SQLite by default at `backend/nextstep.db`.
- App startup loads artifacts into memory through `ArtifactRegistry`.
- The health endpoints report both database and artifact status.
- The outcomes endpoint expects a strict payload with `program_family`, `destination_country`, and `institution_tier`.
- The repo currently treats the checked-in data as part of the reproducible build surface, so keep source files and generated outputs aligned when the pipeline changes.
- Architecture, request flow, and peer handoff notes are documented in the `docs/` folder.

## Troubleshooting

If the server fails to start, check the following first:

- dependencies are installed in the active virtual environment
- `PYTHONPATH` includes `backend`
- the raw data files still exist under `data/raw/`
- the processed artifacts exist under `data/processed/` or have been rebuilt

If the outcomes pipeline produces unexpected results, rebuild the artifacts from scratch and compare the resulting files in `data/processed/`.

## Suggested Next Steps

- Add automated tests for the outcomes ingestion and inference paths
- Document any new raw data sources as they are added
- Consider a small CLI wrapper for starting the API and rebuilding artifacts
