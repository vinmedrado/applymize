from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from backend.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.exception("database_integrity_error")
    return JSONResponse(status_code=409, content={"detail": "Conflito de dados ou registro duplicado"})


async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("unhandled_error")
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor"})
