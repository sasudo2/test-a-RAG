from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"

    class Config:
        env_file = ".env"

setting = Settings()