from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Engineering Knowledge Assistant"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "A production-style AI Engineering Knowledge Assistant"
    DATABASE_URL: str

    # LLM Gateway settings
    DEFAULT_LLM_PROVIDER: str = "openai_dummy" # e.g., "openai_dummy", "gemini_dummy", "anthropic_dummy"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
