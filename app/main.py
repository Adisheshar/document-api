# app/main.py

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.documents.router import router as documents_router

from app.db.base import Base
from app.db.session import engine
from app.core.logging import get_logger, logging_middleware

logger = get_logger(__name__)

def create_application() -> FastAPI:
    app = FastAPI(
        title="Document Lifecycle Management API",
        version="1.0.0",
    )

    # ✅ Use function-based middleware
    app.middleware("http")(logging_middleware)

    # ✅ Include routers
    app.include_router(auth_router)
    app.include_router(documents_router)

    return app


app = create_application()


@app.on_event("startup")
def on_startup() -> None:
    # ✅ Ensure uploads folder exists
    os.makedirs("./uploads", exist_ok=True)
    logger.info("Uploads folder ready at ./uploads")

    # ✅ Create database tables if not exists
    logger.info("Starting application and creating database tables if needed")
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    """Simple health check endpoint"""
    return {"status": "ok"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors"""
    logger.exception(
        "Unhandled exception",
        extra={"path": request.url.path},
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.get("/", tags=["system"])
def root():
    return {"message": "Document Lifecycle Management API is running"}

