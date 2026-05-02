# NextStep Backend Runbook

## 1. Setup & Installation
The project uses a virtual environment located in the root directory.

```powershell
# Activate venv (Windows)
.\venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt
```

## 2. Running the Server
The server runs on FastAPI and Uvicorn.

```powershell
# From the root directory
$env:PYTHONPATH='backend'
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000` and `http://localhost:8000/api/v1`.
Swagger docs: `http://localhost:8000/docs`.
Health checks: `http://localhost:8000/health` and `http://localhost:8000/api/v1/health`.

## 3. Running Tests
Tests are located in `backend/tests` and use `pytest`.

```powershell
# Run all tests
$env:PYTHONPATH='backend'
.\venv\Scripts\pytest.exe backend/tests
```

## 4. Key Demo Credentials
| User Role | Email | Password |
| :--- | :--- | :--- |
| **Student** | `priya@example.com` | `password123` |
| **Underwriter** | `underwriter@nextstep.com` | `uwpass` |
| **Portfolio Manager** | `manager@nextstep.com` | `pmpass` |

## 5. Health Check
Monitor system health at `GET /api/v1/health`.
Verify that `database.status` is `ok` and `artifacts` contains the loaded ML snapshots.
