from fastapi import FastAPI
from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.knowledge_bases import router as kbs_router
from app.api.v1.documents import router as docs_router
from app.api.v1.search import router as search_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)

app.include_router(health_router, prefix="/v1", tags=["Health"])
app.include_router(users_router, prefix="/v1", tags=["Users"])
app.include_router(kbs_router, prefix="/v1", tags=["Knowledge Bases"])
app.include_router(docs_router, prefix="/v1", tags=["Documents"])
app.include_router(search_router, prefix="/v1", tags=["Search"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to AI Engineering Knowledge Assistant"}

