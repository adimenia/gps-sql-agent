from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.health import router as health_router
from app.api.periods import router as periods_router
from app.api.dashboard import router as dashboard_router
from app.api.chat import router as chat_router

app = FastAPI(
    title="Sports Analytics Platform",
    description="Sports analytics platform with Catapult data ingestion and SQL agent",
    version="0.1.0",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(periods_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Sports Analytics Platform API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "database_configured": bool(settings.postgres_host),
        "catapult_configured": bool(settings.catapult_api_token)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )