from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Engineering Knowledge Assistant"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "A production-style AI Engineering Knowledge Assistant"
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
