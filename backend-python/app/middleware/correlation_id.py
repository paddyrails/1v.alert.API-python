"""Correlation ID middleware: accept X-Correlation-Id or generate UUID, add to response and logs."""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import set_correlation_id, get_correlation_id
import logging

logger = logging.getLogger(__name__)
CORRELATION_ID_HEADER = "X-Correlation-Id"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        set_correlation_id(correlation_id)
        request.state.correlation_id = correlation_id
        request.state.start_time = time.perf_counter()
        response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        duration_ms = (time.perf_counter() - request.state.start_time) * 1000
        log_extra = {
            "path": request.url.path,
            "method": request.method,
            "statusCode": response.status_code,
            "durationMs": round(duration_ms, 2),
        }
        logger.info(
            "request_completed",
            extra=log_extra,
        )
        return response
