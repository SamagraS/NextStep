import os
import tempfile
from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

# Set up test environment variables before importing app
# Note: get_settings is cached with @lru_cache, so we must set this before main is imported.
os.environ["NEXTSTEP_DATABASE_URL"] = os.path.join(tempfile.gettempdir(), "nextstep_test.db")

from app.main import app as main_app, lifespan

@pytest_asyncio.fixture(scope="function")
async def test_app() -> AsyncGenerator[FastAPI, None]:
    # We use lifespan explicitly to ensure app state is initialized
    async with lifespan(main_app):
        yield main_app


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
def mock_artifacts(monkeypatch):
    """
    Simulate missing ML models to test the deterministic fallback logic.
    We monkeypatch ArtifactRegistry.load to be a no-op or partial.
    Actually, to make this available per-test, we should scope it to function.
    """
    pass

@pytest.fixture(scope="function")
def patch_artifacts(monkeypatch):
    from app.services.artifact_loader import ArtifactRegistry
    
    def mock_load(self):
        # Do not load ML models
        self.xgb_model = None
        self.scaler = None
        # the fallback doesn't need them
    
    monkeypatch.setattr(ArtifactRegistry, "load", mock_load)
