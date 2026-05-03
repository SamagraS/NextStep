# NextStep Setup & Running Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Virtual environment (included in repo as `venv/`)

## Backend Setup

### 1. Activate Virtual Environment

```powershell
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

## Running the Backend

From the repo root, run:

```powershell
cd backend
..\..\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Or from the root with the `--app-dir` flag:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

**Backend URL**: `http://localhost:8000`

- **Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **API v1**: `http://localhost:8000/api/v1`

## Running the Frontend

From the `Frontend/` directory:

```powershell
npm install  # First time only
npm run dev
```

**Frontend URL**: `http://localhost:5173` (or as shown in terminal)

## Running Tests

From the repo root:

```powershell
# All tests
.\venv\Scripts\python.exe -m pytest

# Specific test file
.\venv\Scripts\python.exe -m pytest tests/api/test_score.py -v

# Quick test
.\venv\Scripts\python.exe -m pytest -q
```

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | `priya@example.com` | `password123` |
| Underwriter | `underwriter@nextstep.com` | `uwpass` |
| Portfolio Manager | `manager@nextstep.com` | `pmpass` |

## Environment Variables

Key settings are in `backend/app/core/config.py`. For local development:

- `DATABASE_URL`: Points to local SQLite
- `ARTIFACTS_DIR`: Generated lookup tables directory
- `API_V1_PREFIX`: Default `/api/v1`

## Troubleshooting

### Backend won't start with `ModuleNotFoundError: No module named 'app'`
→ Make sure you're using `--app-dir backend` or running from the `backend/` directory with a relative import.

### Frontend shows "Backend unavailable"
→ Ensure backend is running on `http://localhost:8000`.

### Tests timeout on async operations
→ Run specific test files individually instead of the full suite.

## Project Structure

See [architecture.md](architecture.md) for detailed backend module documentation.
See [flow.md](flow.md) for request/response flow documentation.
