from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuración cargada desde .env"""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
