"""app/core/logging/__init__.py

Public API for the logging module.

Quick start
-----------
Once at application startup (e.g. inside the FastAPI lifespan):

    from app.core.logging import configure
    configure()                        # reads LOG_LEVEL and LOG_FORMAT env vars
    configure(level="DEBUG")           # override programmatically
    configure(format_="json")          # structured JSON output

Per module — mirrors the standard library pattern:

    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("server started")
    logger.error("something broke", exc_info=True)

Adding request-scoped context (e.g. inside a FastAPI middleware):

    from app.core.logging import bind, unbind, bound_context

    # manual
    token = bind(request_id="abc-123", user_id="usr-42")
    try:
        response = await call_next(request)
    finally:
        unbind(token)

    # or with the context manager
    with bound_context(request_id="abc-123"):
        logger.info("handling request")   # context fields appear automatically
"""

import logging

from app.core.logging._config import build_uvicorn_log_config, configure
from app.core.logging._context import bind, bound_context, get_context, unbind
from app.core.logging._formatters import JSONFormatter, PrettyFormatter

__all__ = [
	"get_logger",
	"configure",
	"bind",
	"unbind",
	"get_context",
	"bound_context",
	"build_uvicorn_log_config",
	"PrettyFormatter",
	"JSONFormatter",
]


def get_logger(name: str) -> logging.Logger:
	"""
	Return a stdlib Logger for the given module name.

	Always pass ``__name__`` so the logger hierarchy mirrors the package
	structure and level filtering works as expected.

	Handlers live exclusively on the root logger (configured once by
	``configure()``), so calling ``get_logger`` multiple times never
	duplicates output.

	Args:
	    name: Typically ``__name__`` of the calling module.

	Returns:
	    A standard :class:`logging.Logger` instance.

	Example:
	    logger = get_logger(__name__)
	    logger.info("User registered")
	    logger.debug("payload: %s", payload)   # lazy — only formatted if DEBUG
	    logger.exception("Unexpected error")   # attaches current traceback
	"""
	return logging.getLogger(name)
