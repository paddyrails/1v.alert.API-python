"""Consistent error response shape and HTTP exception types."""

from typing import Any

from fastapi import HTTPException


ERROR_SHAPE = {
    "error": {
        "code": "string",
        "message": "string",
        "details": {},
    }
}


def error_response(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


class AppError(HTTPException):
    """Base for app errors that map to standard error shape."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=error_response(code, message, details))
        self.code = code
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str | None = None) -> None:
        msg = f"{resource} not found" + (f": {identifier}" if identifier else "")
        super().__init__(404, "NOT_FOUND", msg, {"resource": resource})


class ConflictError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(409, "CONFLICT", message, details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Invalid or missing authentication") -> None:
        super().__init__(401, "UNAUTHORIZED", message)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(403, "FORBIDDEN", message)
