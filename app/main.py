import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware # New: Import CORSMiddleware
from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.knowledge_bases import router as kbs_router
from app.api.v1.documents import router as docs_router
from app.api.v1.search import router as search_router
from app.api.v1.rag import router as rag_router
from app.api.v1.query_executions import router as queries_router
from app.api.v1.auth import router as auth_router # New: Authentication router
from app.core.config import settings
from app.core.observability import configure_opentelemetry_tracing, configure_structured_logging, setup_prometheus_metrics, tracer

# Configure structured logging early
configure_structured_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)

@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "traceparent"],
)

# Configure OpenTelemetry tracing
configure_opentelemetry_tracing(app)

# Setup Prometheus metrics
setup_prometheus_metrics(app)

app.include_router(health_router, prefix="/v1", tags=["Health"])
app.include_router(users_router, prefix="/v1", tags=["Users"])
app.include_router(kbs_router, prefix="/v1", tags=["Knowledge Bases"])
app.include_router(docs_router, prefix="/v1", tags=["Documents"])
app.include_router(search_router, prefix="/v1", tags=["Search"])
app.include_router(rag_router, prefix="/v1", tags=["RAG"])
app.include_router(queries_router, prefix="/v1", tags=["Query History"])
app.include_router(auth_router, prefix="/v1", tags=["Authentication"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
