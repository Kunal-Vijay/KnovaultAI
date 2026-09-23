from fastapi import FastAPI
from app.api.v1.health import router as health_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)

app.include_router(health_router, prefix="/v1", tags=["Health"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to AI Engineering Knowledge Assistant"}
