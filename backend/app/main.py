from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes import health
from app.core.config import get_settings
from app.db.database import Database
from app.services.artifact_loader import ArtifactRegistry
from app.services.auth import AuthService
from app.services.demo_store import DemoStore
from app.services.notifier import DemoNotifier
from app.services.persistence import PersistenceService


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

    # Seed demo users
    auth_service = AuthService(settings)
    persistence = PersistenceService(database)
    await persistence.seed_demo_users(auth_service)
    
    # Seed other demo records and sync back to DemoStore
    await persistence.seed_all(demo_store)
    
    students_db = await persistence.get_all_students()
    cohorts_db = await persistence.get_all_cohorts()
    alerts_db = await persistence.get_all_alerts()
    actions_by_student = {}
    for s in students_db:
        actions_by_student[s["id"]] = await persistence.get_all_student_actions(s["id"])
    
    demo_store.sync_from_persistence(students_db, cohorts_db, alerts_db, actions_by_student)

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
