"""app/core/logging/_config.py

Global logging setup — call configure() exactly once at application startup.
All module-level loggers propagate to root and inherit this configuration.
"""

import logging
from typing import Any

from app.core.config import settings
from app.core.logging._formatters import JSONFormatter, PrettyFormatter

__all__ = ["configure", "build_uvicorn_log_config"]

type LogLevelStr = str
type LogFormat = str  # "pretty" | "json"

# Third-party loggers that are too verbose at their default level
_NOISY_LOGGERS: frozenset[str] = frozenset(
	{"httpx", "httpcore", "asyncio", "watchfiles", "multipart"}
)


def configure(
	*,
	level: LogLevelStr | None = None,
	format_: LogFormat | None = None,
) -> None:
	"""
	Configure the root logger. Must be called once at application startup.

	Priority (highest → lowest):
	    1. Argument passed directly to configure()
	    2. LOG_LEVEL / LOG_FORMAT environment variables
	    3. Defaults: level=INFO, format_=pretty

	Args:
	    level:   Log level string — DEBUG | INFO | WARNING | ERROR | CRITICAL.
	    format_: Output format — "pretty" (colored terminal) | "json" (structured).

	Example:
	    configure(level="DEBUG", format_="json")
	    configure()  # reads LOG_LEVEL and LOG_FORMAT from environment
	"""
	level_str: str = level or settings.LOG_LEVEL
	fmt_str: str = format_ or settings.LOG_FORMAT

	log_level: int = getattr(logging, level_str, logging.INFO)

	match fmt_str:
		case "json":
			formatter: logging.Formatter = JSONFormatter()
		case _:
			formatter = PrettyFormatter()

	handler: logging.StreamHandler[Any] = logging.StreamHandler()
	handler.setLevel(log_level)
	handler.setFormatter(formatter)

	root: logging.Logger = logging.getLogger()
	root.setLevel(log_level)
	# Clear before adding to prevent handler duplication on hot-reload
	root.handlers.clear()
	root.addHandler(handler)

	# Silence chatty third-party loggers unless explicitly debugging them
	for name in _NOISY_LOGGERS:
		logging.getLogger(name).setLevel(logging.WARNING)


def build_uvicorn_log_config(
	*,
	level: LogLevelStr = "INFO",
) -> dict[str, Any]:
	"""
	Returns a logging dictConfig for uvicorn that uses our PrettyFormatter,
	keeping uvicorn and application logs visually consistent.

	Pass the result directly to uvicorn.run(log_config=...).

	Args:
	    level: Minimum log level for uvicorn loggers.

	Example:
	    uvicorn.run("app.main:app", log_config=build_uvicorn_log_config())
	"""
	return {
		"version": 1,
		"disable_existing_loggers": False,
		"formatters": {
			"app": {
				"()": "app.core.logging._formatters.PrettyFormatter",
			},
		},
		"handlers": {
			"default": {
				"class": "logging.StreamHandler",
				"formatter": "app",
				"stream": "ext://sys.stderr",
			},
		},
		"loggers": {
			"uvicorn": {
				"handlers": ["default"],
				"level": level,
				"propagate": False,
			},
			"uvicorn.error": {
				"handlers": ["default"],
				"level": level,
				"propagate": False,
			},
			"uvicorn.access": {
				"handlers": ["default"],
				"level": level,
				"propagate": False,
			},
		},
	}
