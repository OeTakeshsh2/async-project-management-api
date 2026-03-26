from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException
from pydantic_settings import BaseSettings

# Improve
# Mejorar diferenciacion de errores , token expired, invalid token, etc.
# Mejorar tipado
# Agregar sub 


class Settings(BaseSettings):
    database_url:str
    secret_key:str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


    class Config:
        env_file = ".env"

settings = Settings()

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode.update({"exp": expire})

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

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
