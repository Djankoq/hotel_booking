import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # По умолчанию SQLite для быстрого старта локально.
    # В Docker переопределяется на Postgres.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./booking_dev.sqlite")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()