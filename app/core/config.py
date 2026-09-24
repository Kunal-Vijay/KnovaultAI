from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Engineering Knowledge Assistant"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "A production-style AI Engineering Knowledge Assistant"
    DATABASE_URL: str

    # LLM Gateway settings
    DEFAULT_LLM_PROVIDER: str = "openai_dummy" # e.g., "openai_dummy", "gemini_dummy", "anthropic_dummy"

    # Observability settings
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4317"
    OTEL_SERVICE_NAME: str = "fastapi-app"

    # Evaluation settings
    EVALUATION_DATASET_PATH: str = "../evals/dataset/dataset.json"
    EVALUATION_BASELINE_PATH: str = "../evals/baseline/results.json"

    # Security settings
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY" # IMPORTANT: Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # For JWT token expiration

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
