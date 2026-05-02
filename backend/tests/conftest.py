import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings
from app.db.database import Database
from app.services.demo_store import DemoStore

@pytest.fixture(scope="session")
def settings():
    return get_settings()

@pytest.fixture(scope="function")
def test_app():
    # Use the real app but we can override state if needed
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
async def db(settings):
    database = Database(settings.database_url)
    await database.initialize()
    yield database
    await database.close()

@pytest.fixture(scope="function")
def store():
    return DemoStore()
