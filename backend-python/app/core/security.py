"""Password hashing and JWT (access + hashed refresh token) handling."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: UUID, email: str) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_access_expires_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret,
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
        algorithms=["HS256"],
    )


def generate_refresh_token_string() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(user_id: UUID) -> tuple[str, datetime]:
    """Return (raw_token, expires_at). Store only hash in DB."""
    settings = get_settings()
    raw = generate_refresh_token_string()
    expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expires_days)
    return raw, expires_at


def decode_refresh_token_payload(token: str) -> dict:
    """Validate refresh token JWT if we ever store JWT refresh; here we use opaque tokens."""
    raise NotImplementedError("Refresh tokens are opaque; validate via DB only.")
