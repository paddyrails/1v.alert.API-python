"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refreshToken: str = Field(..., alias="refreshToken")

    model_config = {"populate_by_name": True}

    @field_validator("refreshToken", mode="before")
    @classmethod
    def accept_refresh_token(cls, v: str) -> str:
        return v or ""


class LogoutRequest(BaseModel):
    refreshToken: str = Field(..., alias="refreshToken")

    model_config = {"populate_by_name": True}


class TokenResponse(BaseModel):
    accessToken: str = Field(..., alias="accessToken")
    refreshToken: str = Field(..., alias="refreshToken")
    tokenType: str = Field(default="bearer", alias="tokenType")
    user: UserResponse

    model_config = {"populate_by_name": True}


# For response construction
def token_response(access_token: str, refresh_token: str, user: UserResponse) -> dict:
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "bearer",
        "user": user.model_dump(),
    }
