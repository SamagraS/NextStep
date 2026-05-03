from app.schemas.common import StrictSchema


class Token(StrictSchema):
    access_token: str
    token_type: str
    role: str
    full_name: str
    email: str


class TokenData(StrictSchema):
    email: str | None = None
    role: str | None = None


class LoginRequest(StrictSchema):
    email: str
    password: str
