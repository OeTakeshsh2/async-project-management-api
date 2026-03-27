from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict

# Improve
# Mejorar diferenciacion de errores , token expired, invalid token, etc.
# Mejorar tipado
# Agregar sub 


class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB:str

    algorithm: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30
    

    model_config=SettingsConfigDict(
        env_file = ".env",
        extra="ignore"
    )

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
