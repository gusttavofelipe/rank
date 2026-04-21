"""app/main.py"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.category import router as category_router
from app.api.v1.routers.country import router as country_router
from app.api.v1.routers.user import router as user_router
from app.core.config import settings
from app.core.exceptions.db import DatabaseConnectionError
from app.core.exceptions.handler import register_exception_handlers
from app.core.logging import build_uvicorn_log_config, configure, get_logger
from app.core.middlewares.language import LanguageMiddleware
from app.core.middlewares.request_context import RequestContextMiddleware
from app.infra.db.manager import DatabaseManager

configure()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
	"""Manages application startup and shutdown."""
	try:
		await DatabaseManager.test_connection()
	except Exception as exc:
		raise DatabaseConnectionError(message=f"Unable to connect to the database: {exc}")
	logger.info("Database healthy")

	yield

	logger.info("Application shutting down")


class App(FastAPI):
	"""Custom FastAPI application class."""

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		"""Initializes the FastAPI application with default settings and lifespan."""
		super().__init__(
			*args,
			**kwargs,
			title=settings.APP_TITLE,
			version=settings.APP_VERSION,
			description=settings.APP_DESCRIPTION,
			lifespan=lifespan,
		)
		self.__include_routers()
		self.__register_exception_handlers()
		self.__add_middlewares()

	def __register_exception_handlers(self) -> None:
		"""Registers all mapped exception handlers for the application."""
		register_exception_handlers(app=self)

	def __add_middlewares(self) -> None:
		"""Includes all predefined API middlewares into the application.

		Order matters — middlewares wrap the request in LIFO order, so the last
		one added is the outermost wrapper.  RequestContextMiddleware should be
		outermost so request_id is available to every subsequent layer.
		"""
		self.add_middleware(middleware_class=LanguageMiddleware)
		self.add_middleware(middleware_class=RequestContextMiddleware)

	def __include_routers(self) -> None:
		"""Includes all predefined API routers into the application."""
		self.include_router(router=auth_router)
		self.include_router(router=category_router)
		self.include_router(router=user_router)
		self.include_router(router=country_router)


app: FastAPI = App()


if __name__ == "__main__":
	uvicorn.run(
		"app.main:app",
		host="0.0.0.0",
		port=8001,
		log_config=build_uvicorn_log_config(level=settings.APP_VERSION and "INFO"),
		reload=True,
		env_file=".env",
	)
