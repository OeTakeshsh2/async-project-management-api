import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select, delete, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base


class Settings(BaseSettings):
    """Configuración cargada desde .env"""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()


# ==================== MODELO DE TOKENS ====================
class UserToken(Base):
    """Tabla para almacenar hashes de refresh tokens activos (revocación + single session)"""
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ==================== HELPERS ====================
def _base_user_payload(user) -> dict:
    return {"sub": user.email, "user_id": user.id}


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ==================== CREACIÓN DE TOKENS ====================
def create_access_token(data: dict) -> str:
    if "sub" not in data or "user_id" not in data:
        raise ValueError("El payload requiere 'sub' y 'user_id'.")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    if "sub" not in data or "user_id" not in data:
        raise ValueError("El payload requiere 'sub' y 'user_id'.")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_user_access_token(user) -> str:
    return create_access_token(_base_user_payload(user))


def create_user_refresh_token(user) -> str:
    return create_refresh_token(_base_user_payload(user))


# ==================== OPERACIONES EN DB ====================
async def store_refresh_token(db: AsyncSession, user_id: int, token: str):
    """Guarda hash del refresh token y elimina el anterior (single session)"""
    refresh_hash = hash_token(token)
    await db.execute(delete(UserToken).where(UserToken.user_id == user_id))

    user_token = UserToken(user_id=user_id, token_hash=refresh_hash)
    db.add(user_token)
    await db.commit()


async def verify_refresh_token(db: AsyncSession, user_id: int, token: str) -> bool:
    """Verifica que el hash del refresh token exista en la DB"""
    token_hash = hash_token(token)
    result = await db.execute(
        select(UserToken).where(
            UserToken.user_id == user_id,
            UserToken.token_hash == token_hash
        )
    )
    return result.scalar_one_or_none() is not None


# ==================== DECODIFICACIÓN ====================
def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Tipo de token inválido: se esperaba {expected_type}"
            )

        if "user_id" not in payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El payload del token está incompleto"
            )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"El token de {expected_type} ha expirado"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar la firma del token"
        )


def decode_access_token(token: str) -> dict:
    return decode_token(token, "access")


def decode_refresh_token(token: str) -> dict:
    return decode_token(token, "refresh")
