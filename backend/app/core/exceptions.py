# backend/app/core/exceptions.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union

class TwinFlowException(Exception):
    """Base exception for TwinFlow."""
    def __init__(self, message: str, status_code: int = 400, detail: Union[str, dict, list] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(message)

class NotFoundError(TwinFlowException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class AuthenticationError(TwinFlowException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(TwinFlowException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)

class ValidationError(TwinFlowException):
    def __init__(self, message: str = "Validation error", detail: Union[str, dict, list] = None):
        super().__init__(message, status_code=422, detail=detail)

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(TwinFlowException)
    async def twinflow_exception_handler(request: Request, exc: TwinFlowException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.message,
                "detail": exc.detail,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "Validation error",
                "detail": exc.errors(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Log the exception here
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

# Import datetime for timestamp
from datetime import datetime