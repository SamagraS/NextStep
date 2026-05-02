# Backend Architecture

This document explains the backend modules in `backend/app` and the role each one plays in the application.

## Application Entry Point

### `backend/app/main.py`
Creates the FastAPI application, wires the startup and shutdown lifecycle, loads settings, initializes the SQLite database, loads generated artifacts, and attaches shared runtime objects to `app.state`.

## API Layer

### `backend/app/api/routes/auth.py`
Handles demo login by verifying credentials, resolving the display name for the authenticated user, and returning a signed token response.

### `backend/app/api/router.py`
Builds the top-level API router and mounts the functional route groups under `/api/v1`.

### `backend/app/api/routes/health.py`
Exposes health and readiness endpoints for the application, database, and artifact state.

### `backend/app/api/routes/score.py`
Handles origination scoring requests, latest-score lookup, and streaming score updates.

### `backend/app/api/routes/student.py`
Serves student dashboard data and action-completion endpoints.

### `backend/app/api/routes/portfolio.py`
Supports portfolio dashboard, cohort, alert, and rescore operations.

### `backend/app/api/routes/outcomes.py`
Exposes the outcomes prediction endpoint used for placement, salary, and risk forecasting.

## Configuration and Core Settings

### `backend/app/core/config.py`
Defines the application settings model, environment-variable loading, and default paths for the database, data directories, artifacts, and API prefix.

## Persistence and Database

### `backend/app/db/database.py`
Owns SQLite connection setup, initialization, and shutdown behavior for the local application database.

### `backend/app/db/schema.py`
Defines the database schema and table creation helpers used during startup.

## Authentication and Persistence

### `backend/app/services/auth.py`
Creates and verifies demo access tokens used by the login route.

### `backend/app/services/persistence.py`
Reads and writes user, demo, and portfolio state against the SQLite-backed store.

## Domain Models

### `backend/app/models/feature_assembly.py`
Defines the feature-assembly data structures used by the scoring flow, including encoded fields and resolved feature bundles.

## Outcomes Pipeline

### `backend/app/outcomes/ingestion.py`
Loads raw datasets from `data/raw/`, including HESA, QILT, Eurostat, Eurostat salary, BLS, OFLC, NIRF, StatsCan, and World Bank inputs. It normalizes input formats into raw data frames that the preprocessing layer can standardize.

### `backend/app/outcomes/preprocessing.py`
Converts raw ingested data into standardized placement, salary, macro, and microdata tables. This is where source-specific rows are normalized into the common shape used by the model builders.

### `backend/app/outcomes/mapping.py`
Contains taxonomy and program-family mapping utilities. It translates country, SOC, HESA, QILT, and program labels into the canonical program-family vocabulary.

### `backend/app/outcomes/inference.py`
Builds processed lookup artifacts, writes the manifest, and loads those artifacts at prediction time to produce outcomes forecasts.

### `backend/app/outcomes/models/macro.py`
Builds macroeconomic adjustment tables from country-level unemployment inputs.

### `backend/app/outcomes/models/placement.py`
Builds placement lookup tables from standardized employment inputs and combines source data across countries and tiers.

### `backend/app/outcomes/models/salary.py`
Builds salary lookup tables from standardized salary inputs and microdata-backed wage sources.

## Service Layer

### `backend/app/services/artifact_loader.py`
Loads runtime artifact snapshots from the artifacts directory and reports their health for the API.

### `backend/app/services/contract_examples.py`
Stores example request and response payloads for contract testing and documentation.

### `backend/app/services/demo_store.py`
Keeps in-memory demo state used by the scoring and dashboard flows.

### `backend/app/services/feature_assembly.py`
Assembles features for scoring by combining student input, university lookup data, taxonomy mapping, macro signals, and imputation rules.

### `backend/app/services/notifier.py`
Wraps the demo store and notification behavior used by the student and scoring workflows.

### `backend/app/services/outcomes.py`
Provides service-level access to outcomes inference and artifact-backed prediction helpers.

### `backend/app/services/portfolio_monitor.py`
Tracks portfolio state and supports rescore-related operations.

### `backend/app/services/reference_data.py`
Provides lookup and normalization helpers for universities, programs, countries, and imputation profiles.

### `backend/app/services/scoring.py`
Coordinates origination score calculations and scoring workflow orchestration.

### `backend/app/services/student_dashboard.py`
Builds the student dashboard view model from demo and scoring state.

### `backend/app/services/student_engagement.py`
Tracks student engagement signals and action-completion state.

## Testing

### `backend/tests/`
Contains the current pytest coverage for auth, health, scoring, student, and portfolio flows.

## Shared Schemas

### `backend/app/schemas/common.py`
Defines shared schema types and shared validation primitives used across requests and responses.

### `backend/app/schemas/health.py`
Defines health and artifact-status schemas.

### `backend/app/schemas/outcomes.py`
Defines the outcomes prediction request and response models.

### `backend/app/schemas/portfolio.py`
Defines portfolio-related request and response contracts.

### `backend/app/schemas/score.py`
Defines scoring-related request and response contracts.

### `backend/app/schemas/student.py`
Defines student dashboard and action models.

## Utilities

### `backend/app/utils/time.py`
Provides time helpers used by the API and service layer.

## Scripts

### `backend/build_outcomes_pipeline.py`
Runs the end-to-end rebuild of processed outcomes artifacts.

### `backend/demo_outcomes_example.py`
Runs a sample outcomes prediction and writes the example output file.

### `backend/scripts/fetch_bls_employment.py`
Builds the US employment proxy from OFLC source data.

### `backend/scripts/fetch_eurostat_full.py`
Fetches or prepares the full Eurostat employment source data.

### `backend/scripts/fetch_nirf_batch.py`
Fetches or prepares NIRF batch inputs.

## Additional Docs

- [docs/api_contract.md](api_contract.md)
- [docs/flow.md](flow.md)
- [docs/runbook.md](runbook.md)
