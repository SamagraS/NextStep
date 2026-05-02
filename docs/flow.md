# Backend Flow

This document explains how the backend modules work together today.

## Request Startup Flow

1. `backend/app/main.py` creates the FastAPI app.
2. The lifespan handler loads settings from `backend/app/core/config.py`.
3. `backend/app/db/database.py` initializes the SQLite database.
4. `backend/app/services/artifact_loader.py` loads any prebuilt artifacts from the artifacts directory.
5. Runtime helpers such as the demo store and notifier are attached to `app.state`.
6. `backend/app/api/router.py` mounts the API routes under `/api/v1`.

## Authentication Flow

1. Requests hit `backend/app/api/routes/auth.py`.
2. The route uses `backend/app/services/persistence.py` to load the user by email.
3. `backend/app/services/auth.py` verifies the password and creates the access token.
4. The demo store resolves the display name for student accounts.
5. The response is shaped by `backend/app/schemas/auth.py`.

## API Request Flow

### Health

1. Requests hit `backend/app/api/routes/health.py`.
2. The route reads database and artifact state from `app.state`.
3. The response reports readiness and loaded artifact status.

### Scoring

1. Requests hit `backend/app/api/routes/score.py`.
2. The route layer passes payloads into `backend/app/services/scoring.py`.
3. `backend/app/services/feature_assembly.py` resolves university, taxonomy, macro, and tenacity inputs.
4. `backend/app/services/reference_data.py` resolves lookup data and imputation defaults.
5. `backend/app/services/demo_store.py` stores demo state.
6. `backend/app/services/notifier.py` publishes or records score updates.
7. The response model is shaped by `backend/app/schemas/score.py` and shared schema types.

### Portfolio Views

1. Requests hit `backend/app/api/routes/portfolio.py`.
2. `backend/app/services/portfolio_monitor.py` collects the dashboard, cohort, and alert state.
3. `backend/app/services/persistence.py` supplies stored demo and alert history.
4. `GET /api/v1/portfolio/dashboard`, `GET /api/v1/portfolio/cohorts`, and `GET /api/v1/portfolio/alerts` are handled here.
5. The response is validated by `backend/app/schemas/portfolio.py`.

### Student Dashboard

1. Requests hit `backend/app/api/routes/student.py`.
2. `backend/app/services/student_dashboard.py` collects the current student view model.
3. `backend/app/services/student_engagement.py` tracks completion signals and engagement state.
4. The response is validated by `backend/app/schemas/student.py`.

### Portfolio Rescore

1. Requests hit `backend/app/api/routes/portfolio.py`.
2. `backend/app/services/portfolio_monitor.py` evaluates portfolio state.
3. `backend/app/services/scoring.py` or related helpers recompute the score path.
4. The result is returned through the portfolio schema.

### Outcomes Prediction

1. Requests hit `backend/app/api/routes/outcomes.py`.
2. `backend/app/services/outcomes.py` or the inference layer reads the processed lookup tables.
3. `backend/app/outcomes/inference.py` selects placement, salary, and macro rows.
4. `backend/app/outcomes/mapping.py` is used to normalize program-family and country inputs.
5. The response is composed with `backend/app/schemas/outcomes.py`.

### Health

1. Requests hit `backend/app/api/routes/health.py`.
2. The route reads database and artifact status from `app.state`.
3. The response reports the health of the app, database, and loaded artifacts.

## Outcomes Rebuild Flow

1. `backend/build_outcomes_pipeline.py` starts the rebuild.
2. `backend/app/outcomes/ingestion.py` reads raw data from `data/raw/`.
3. `backend/app/outcomes/preprocessing.py` converts the raw sources into standard placement, salary, macro, and microdata tables.
4. `backend/app/outcomes/models/placement.py`, `salary.py`, and `macro.py` build the lookup artifacts.
5. `backend/app/outcomes/inference.py` writes the lookup CSV files and `source_manifest.json` into `data/processed/`.
6. The API consumes those generated files at runtime.

## Data Dependency Flow

- Raw inputs live in `data/raw/`.
- Canonical mappings live in `data/mappings/`.
- Generated outputs live in `data/processed/`.
- Optional model artifacts live in `artifacts/`.
- The database lives at the configured SQLite path, defaulting to `backend/nextstep.db`.

## Source Families

The outcomes pipeline currently ingests and standardizes these source families:

- HESA
- QILT
- Eurostat
- Eurostat salary
- BLS
- OFLC H1B
- NIRF
- StatsCan
- World Bank

## Current Cross-Module Relationships

- `backend/app/main.py` owns application lifecycle and dependency wiring.
- `backend/app/api/router.py` connects routes to the service layer.
- `backend/app/services/*` contains the orchestration layer used by API endpoints.
- `backend/app/outcomes/*` contains the data pipeline and inference path.
- `backend/app/schemas/*` defines request and response contracts shared by routes and services.
- `backend/app/db/*` manages local persistence.
- `backend/app/core/*` provides configuration values consumed across the app.
