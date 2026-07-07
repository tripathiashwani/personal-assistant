"""
Custom application exceptions and their FastAPI handlers.

Services/repositories raise these domain-specific exceptions instead of
raising HTTPException directly. This keeps the service layer free of
HTTP-specific concerns (status codes, response shape) — routers and this
handler module are the only places that know about HTTP.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for all domain-level application errors."""

    status_code: int = 500
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    message = "Resource not found."


class UnauthorizedError(AppError):
    status_code = 401
    message = "Authentication required."


class ForbiddenError(AppError):
    status_code = 403
    message = "You do not have access to this resource."


class ConflictError(AppError):
    status_code = 409
    message = "Resource already exists."


class ValidationAppError(AppError):
    status_code = 422
    message = "Invalid input."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
