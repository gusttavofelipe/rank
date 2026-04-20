"""app/core/exceptions/handler.py"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions.db import (
	DBOperationError,
	ObjectAlreadyExistError,
	ObjectNotFound,
)


def register_exception_handlers(app: FastAPI) -> None:
	"""Registers global exception handlers for the FastAPI application."""

	@app.exception_handler(DBOperationError)
	def db_operation_error_handler(
		request: Request, exc: DBOperationError
	) -> JSONResponse:
		return JSONResponse(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			content={"error": exc.message},
		)

	@app.exception_handler(ObjectAlreadyExistError)
	def object_already_exist_handler(
		request: Request, exc: ObjectAlreadyExistError
	) -> JSONResponse:
		return JSONResponse(
			status_code=status.HTTP_409_CONFLICT,
			content={"error": exc.message},
		)

	@app.exception_handler(ObjectNotFound)
	def object_not_found_handler(request: Request, exc: ObjectNotFound) -> JSONResponse:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"error": exc.message},
		)

	@app.exception_handler(Exception)
	def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
		error: str = f"Unexpected error [{type(exc).__name__}]: {exc}"
		return JSONResponse(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": error}
		)
