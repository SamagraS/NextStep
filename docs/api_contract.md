# NextStep API Contract

This document reflects the current v1 backend surface exposed by the FastAPI app.

## Base URLs

- `/health`
- `/api/v1`

## Authentication

### `POST /api/v1/auth/login`
Authenticates a demo user and returns a token payload.

Request body: `LoginRequest` from [backend/app/schemas/auth.py](../backend/app/schemas/auth.py).

Response body: `Token` from [backend/app/schemas/auth.py](../backend/app/schemas/auth.py).

Response fields:

- `access_token`
- `token_type`
- `role`
- `full_name`

## Health

### `GET /health`
### `GET /api/v1/health`
Returns `HealthResponse` from [backend/app/schemas/health.py](../backend/app/schemas/health.py).

## Scoring

### `POST /api/v1/score/origination`
Returns `ScoringResponse` from [backend/app/schemas/score.py](../backend/app/schemas/score.py).

Request body: `OriginationScoringRequest`.

### `GET /api/v1/score/{application_id}/latest`
Returns `ScoreLatestResponse` from [backend/app/schemas/score.py](../backend/app/schemas/score.py).

### `GET /api/v1/score/{application_id}/stream`
SSE endpoint that emits `SSEStudentProfileUpdatedEvent` and `SSEHeartbeatEvent` from [backend/app/schemas/health.py](../backend/app/schemas/health.py).

## Student

### `GET /api/v1/student/dashboard/{student_id}`
Returns `StudentDashboardResponse` from [backend/app/schemas/student.py](../backend/app/schemas/student.py).

### `POST /api/v1/student/action/complete`
Accepts `StudentActionCompleteRequest` from [backend/app/schemas/student.py](../backend/app/schemas/student.py) and returns an empty success response.

## Portfolio

### `GET /api/v1/portfolio/dashboard`
Returns `PortfolioDashboardResponse` from [backend/app/schemas/portfolio.py](../backend/app/schemas/portfolio.py).

### `GET /api/v1/portfolio/cohorts`
Returns `list[CohortRow]`.

### `GET /api/v1/portfolio/alerts`
Returns `list[CohortAlert]`.

### `POST /api/v1/portfolio/rescore`
Returns `202 Accepted` after the demo rescore completes.

## Outcomes

### `POST /api/v1/outcomes/predict`
Returns `OutcomePredictionResponse` from [backend/app/schemas/outcomes.py](../backend/app/schemas/outcomes.py).

Request body: `OutcomePredictionRequest`.
