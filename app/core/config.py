from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Engineering Knowledge Assistant"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "A production-style AI Engineering Knowledge Assistant"
    DATABASE_URL: str

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # Ingestion / storage
    LOCAL_STORAGE_DIR: str = "./data/documents"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # LLM Gateway settings
    DEFAULT_LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    OPENROUTER_FALLBACK_MODELS: str = ""
    OPENROUTER_BYOK_PROVIDERS: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_TIMEOUT_SECONDS: float = 120.0

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
