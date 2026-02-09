# app/core/logging.py
import json
import logging
import time
import uuid
from typing import Any, Dict

from fastapi import Request
from starlette.responses import Response

# --- JSON Formatter ---
class JsonFormatter(logging.Formatter):
    """Simple JSON formatter for structured logs."""
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)

        return json.dumps(log_record, ensure_ascii=False)

# --- Logger setup ---
def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger

logger = get_logger("app.request")

# --- Middleware function ---
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "http_request",
        extra={
            "extra": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }
        },
    )
    return response
