"""app/core/logging/_formatters.py

Two log formatters:

  PrettyFormatter — colored, human-readable, designed for terminal / development.
  JSONFormatter   — single-line structured JSON for Datadog, Loki, ELK, etc.

Level-based behaviour (matches big-tech observability conventions):
  DEBUG / ERROR / CRITICAL → call site (file:line in func) + traceback when present
  INFO  / WARNING          → clean message only; no location noise
"""

import json
import logging
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from app.core.logging._context import ContextData, get_context

__all__ = ["PrettyFormatter", "JSONFormatter"]

# ── Type aliases (PEP 695) ────────────────────────────────────────────────────

type LogLevel = int

# ── Level sets ────────────────────────────────────────────────────────────────

# Levels that include full stack traces.
_TRACEBACK_LEVELS: frozenset[LogLevel] = frozenset(
	{logging.DEBUG, logging.ERROR, logging.CRITICAL}
)

# ── Shared helpers ────────────────────────────────────────────────────────────


def _is_project_code(record: logging.LogRecord) -> bool:
	"""True when the log record originates from the project's own code,
	not from a third-party library in .venv or site-packages."""
	try:
		rel: Path = Path(record.pathname).relative_to(Path.cwd())
		return not str(rel).startswith(".venv")
	except ValueError:
		return False


def _needs_location(record: logging.LogRecord) -> bool:
	"""Show call site for all levels, but only for project code."""
	return _is_project_code(record)


def _needs_traceback(record: logging.LogRecord) -> bool:
	"""True when a full stack trace should be appended."""
	return record.levelno in _TRACEBACK_LEVELS or bool(record.exc_info)


def _get_location(record: logging.LogRecord) -> str:
	"""
	Returns the call-site as 'path/to/file.py:line in func_name',
	relative to the current working directory when possible.
	"""
	try:
		fp: Path = Path(record.pathname).relative_to(Path.cwd())
	except ValueError:
		fp = Path(record.pathname)
	return f"{fp}:{record.lineno} in {record.funcName}"


def _pretty_ts(record: logging.LogRecord) -> str:
	"""Human-readable timestamp with millisecond precision."""
	base: str = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
	return f"{base}.{int(record.msecs):03d}"


def _iso_ts(record: logging.LogRecord) -> str:
	"""ISO-8601 UTC timestamp suitable for log ingestors."""
	base: str = datetime.fromtimestamp(record.created, tz=UTC).strftime(
		"%Y-%m-%dT%H:%M:%S"
	)
	return f"{base}.{int(record.msecs):03d}Z"


def _format_exc(record: logging.LogRecord) -> str | None:
	"""Returns the formatted exception traceback string, or None."""
	if record.exc_info:
		return "".join(traceback.format_exception(*record.exc_info)).rstrip()
	return None


# ── PrettyFormatter ───────────────────────────────────────────────────────────


class PrettyFormatter(logging.Formatter):
	"""
	Colored human-readable formatter for terminal output.

	INFO / WARNING (clean):
	    [2024-01-15 10:30:45.123] INFO     User registered  [request_id=abc]

	DEBUG / ERROR / CRITICAL (verbose):
	    [2024-01-15 10:30:45.123] ERROR    app/service/user.py:42 in create │ DB error
	      Traceback (most recent call last):
	        ...
	"""

	# ── ANSI escape codes ─────────────────────────────────────────────────────
	GREY: ClassVar[str] = "\x1b[38;20m"
	CYAN: ClassVar[str] = "\x1b[36;20m"
	YELLOW: ClassVar[str] = "\x1b[33;20m"
	RED: ClassVar[str] = "\x1b[31;20m"
	BOLD_RED: ClassVar[str] = "\x1b[31;1m"
	BLUE: ClassVar[str] = "\x1b[34;20m"
	BOLD_GREEN: ClassVar[str] = "\x1b[92m"
	WHITE: ClassVar[str] = "\x1b[37;20m"
	RESET: ClassVar[str] = "\x1b[0m"
	DIM: ClassVar[str] = "\x1b[2m"

	# ── Color maps ────────────────────────────────────────────────────────────
	LEVEL_COLORS: ClassVar[dict[int, str]] = {
		logging.DEBUG: "\x1b[34;20m",  # blue
		logging.INFO: "\x1b[92m",  # bold green
		logging.WARNING: "\x1b[33;20m",  # yellow
		logging.ERROR: "\x1b[31;20m",  # red
		logging.CRITICAL: "\x1b[31;1m",  # bold red
	}

	MESSAGE_COLORS: ClassVar[dict[int, str]] = {
		logging.DEBUG: "\x1b[38;20m",  # grey
		logging.INFO: "\x1b[36;20m",  # cyan
		logging.WARNING: "\x1b[33;20m",  # yellow
		logging.ERROR: "\x1b[31;20m",  # red
		logging.CRITICAL: "\x1b[31;1m",  # bold red
	}

	# ── Private helpers ───────────────────────────────────────────────────────

	def _lc(self, levelno: int) -> str:
		return self.LEVEL_COLORS.get(levelno, self.GREY)

	def _mc(self, levelno: int) -> str:
		return self.MESSAGE_COLORS.get(levelno, self.RESET)

	def _render_ctx(self) -> str:
		"""Renders the current context fields as a dimmed suffix, or ''."""
		ctx: ContextData = get_context()
		if not ctx:
			return ""
		pairs: list[str] = [f"{k}={v}" for k, v in ctx.items()]
		return f"  {self.DIM}[{' '.join(pairs)}]{self.RESET}"

	# ── Public interface ──────────────────────────────────────────────────────

	def format(self, record: logging.LogRecord) -> str:
		ts: str = _pretty_ts(record)
		lc: str = self._lc(record.levelno)
		mc: str = self._mc(record.levelno)

		ts_s: str = f"[{self.WHITE}{ts}{self.RESET}]"
		lvl_s: str = f"{lc}{record.levelname:<8}{self.RESET}"
		msg_s: str = f"{mc}{record.getMessage()}{self.RESET}"
		ctx_s: str = self._render_ctx()

		if _needs_location(record):
			loc: str = f"{self.DIM}{_get_location(record)}{self.RESET}"
			sep: str = f"{self.DIM}│{self.RESET}"
			line: str = f"{ts_s} {lvl_s} {loc} {sep} {msg_s}{ctx_s}"
		else:
			line = f"{ts_s} {lvl_s} {msg_s}{ctx_s}"

		exc: str | None = _format_exc(record)
		if exc and _needs_traceback(record):
			return f"{line}\n{self.DIM}{exc}{self.RESET}"
		return line


# ── JSONFormatter ─────────────────────────────────────────────────────────────


class JSONFormatter(logging.Formatter):
	"""
	Single-line JSON formatter for production log ingestors.

	INFO / WARNING:
	    {"ts":"...","level":"INFO","logger":"app.service","msg":"User registered",
	     "request_id":"abc","user_id":"42"}

	DEBUG / ERROR / CRITICAL (adds location and optional exc_info):
	    {"ts":"...","level":"ERROR","logger":"app.service","msg":"DB error",
	     "location":"app/service/user.py:42 in create","exc_info":"Traceback..."}
	"""

	def format(self, record: logging.LogRecord) -> str:
		payload: dict[str, Any] = {
			"ts": _iso_ts(record),
			"level": record.levelname,
			"logger": record.name,
			"msg": record.getMessage(),
		}

		if _needs_location(record):
			payload["location"] = _get_location(record)

		if _needs_traceback(record):
			exc: str | None = _format_exc(record)
			if exc:
				payload["exc_info"] = exc

		# Merge context fields (request_id, user_id, etc.) into the top level.
		ctx: ContextData = get_context()
		if ctx:
			payload |= ctx  # type: ignore[arg-type]

		return json.dumps(payload, ensure_ascii=False, default=str)
