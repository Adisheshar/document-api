#app/core/config
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_URL: str = f"sqlite:///{BASE_DIR}/app.db"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Document Lifecycle Management"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT
    JWT_SECRET_KEY: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage
    UPLOAD_DIR: Path = Path("./uploads")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()

UPLOAD_DIR = "./uploads"
