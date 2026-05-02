from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.auth import LoginRequest, Token
from app.services.auth import AuthService
from app.services.persistence import PersistenceService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(request: Request, payload: LoginRequest) -> Token:
    settings = request.app.state.settings
    auth_service = AuthService(settings)
    persistence = PersistenceService(request.app.state.database)

    user = await persistence.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth_service.verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Resolve full name for the token response (demo convenience)
    full_name = "User"
    if user["role"] == "student":
        student_id = f"student-{user['email'].split('@')[0]}"
        student = request.app.state.demo_store.get_student(student_id)
        if student:
            full_name = student.full_name
    elif user["role"] == "underwriter":
        full_name = "Senior Underwriter"
    elif user["role"] == "portfolio_manager":
        full_name = "Portfolio Lead"

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
        full_name=full_name,
    )
