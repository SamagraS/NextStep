from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes import health
from app.core.config import get_settings
from app.db.database import Database
from app.services.artifact_loader import ArtifactRegistry
from app.services.demo_store import DemoStore
from app.services.notifier import DemoNotifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    database = Database(settings.database_url)
    await database.initialize()

    artifacts = ArtifactRegistry(settings.artifacts_dir)
    artifacts.load()
    demo_store = DemoStore()
    notifier = DemoNotifier(demo_store)

    app.state.settings = settings
    app.state.database = database
    app.state.artifacts = artifacts
    app.state.demo_store = demo_store
    app.state.notifier = notifier

    try:
        yield
    finally:
        await database.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(health.router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
