"""app/core/logging/config.py"""

from typing import Any

LOGGING_CONFIG: dict[str, Any] = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"default": {
			"()": "app.core.logging.Formatter",
			"use_colors": True,
			"show_path": False,  # For uvicorn logs, it doesn't show the path
		},
	},
	"handlers": {
		"default": {
			"formatter": "default",
			"class": "logging.StreamHandler",
			"stream": "ext://sys.stderr",
		},
	},
	"loggers": {
		"uvicorn": {
			"handlers": ["default"],
			"level": "INFO",
			"propagate": False,
		},
		"uvicorn.error": {
			"handlers": ["default"],
			"level": "INFO",
			"propagate": False,
		},
		"uvicorn.access": {
			"handlers": ["default"],
			"level": "INFO",
			"propagate": False,
		},
	},
}
