from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    app_env: str = "dev"
    upload_dir: Path = Path("data/upload")

    class Config:
        env_file = ".env"

setting = Settings()