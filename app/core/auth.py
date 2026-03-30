from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from fastapi import HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict

# Improve
# Mejorar diferenciacion de errores , token expired, invalid token, etc.
# Mejorar tipado
# Agregar sub 


class Settings(BaseSettings):
    database_url: str
    secret_key: str

    postgres_user: str
    postgres_password: str
    postgres_db: str

    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()

def create_refresh_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.secret_key,algorithm=settings.algorithm)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
        })

    return jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
            )

def decode_access_token(token: str):
    try:
        
        payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
                )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
                statuscode=401,
                details="Token expired"
                )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
