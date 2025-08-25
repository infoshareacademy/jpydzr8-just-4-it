from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    SECRET_KEY: str = "change_me_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SQLITE_PATH: str = "app.db"  # względna ścieżka do pliku bazy
    CORS_ORIGINS: str = "*"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        p = Path(__file__).resolve().parents[2] / self.SQLITE_PATH
        return f"sqlite:///{p}"

    class Config:
        env_file = ".env"

settings = Settings()