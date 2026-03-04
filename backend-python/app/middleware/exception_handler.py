"""Global exception handlers for consistent error shape. Do not leak stack traces in production."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.errors import AppError, error_response
from app.core.logging import get_correlation_id

logger = logging.getLogger(__name__)


def _detail_payload(exc: RequestValidationError) -> dict[str, Any]:
    return {"validation": exc.errors()} if exc.errors() else {}


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response("VALIDATION_ERROR", "Validation failed", _detail_payload(exc)),
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    settings = get_settings()
    correlation_id = get_correlation_id()
    logger.exception(
        "unhandled_exception correlationId=%s path=%s method=%s",
        correlation_id,
        request.url.path,
        request.method,
    )
    message = "Internal server error"
    details: dict[str, Any] = {}
    if settings.debug:
        details["exception"] = str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response("INTERNAL_ERROR", message, details),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
