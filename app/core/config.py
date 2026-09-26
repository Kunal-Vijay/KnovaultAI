from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KnovaultAI — AI Powered Knowledge Assistant"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "KnovaultAI: upload documents, search with hybrid RAG, and get grounded answers."
    DATABASE_URL: str

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # Ingestion / storage
    LOCAL_STORAGE_DIR: str = "./data/documents"
    STORAGE_BACKEND: str = "local"  # local | supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "documents"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # LLM Gateway settings
    DEFAULT_LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = ""
    OPENROUTER_FALLBACK_MODELS: str = ""
    OPENROUTER_BYOK_PROVIDERS: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_TIMEOUT_SECONDS: float = 120.0

    LLM_ROUTING_DEFAULT_PLUG: str = "gemma-26b"
    LLM_ROUTING_QUALITY_PLUG: str = "gemma-31b"
    LLM_ROUTING_FAST_PLUG: str = "gemma-26b"
    LLM_ROUTING_STRONG_SIMILARITY_THRESHOLD: float = 0.35

    QUERY_HISTORY_RETENTION_DAYS: int = 0

    # Observability (Render/PaaS: leave OTEL_TRACES_ENABLED=false and endpoint empty)
    OTEL_TRACES_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_SERVICE_NAME: str = "fastapi-app"

    # Comma-separated browser origins for CORS (include your deployed frontend URL)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080"

    # Evaluation settings
    EVALUATION_DATASET_PATH: str = "../evals/dataset/dataset.json"
    EVALUATION_BASELINE_PATH: str = "../evals/baseline/results.json"

    # Security settings
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY" # IMPORTANT: Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # For JWT token expiration

    # Demo / portfolio login (passwordless JWT for shared demo user)
    DEMO_LOGIN_ENABLED: bool = False
    DEMO_USERNAME: str = "demo"
    ALLOW_PUBLIC_REGISTRATION: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
