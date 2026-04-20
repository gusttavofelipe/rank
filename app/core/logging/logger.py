"""app/core/logging/logger.py"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Self


class Formatter(logging.Formatter):
	"""Style formatter with colors, timestamp and file path"""

	GREY, GREEN, CYAN = "\x1b[38;20m", "\x1b[32;1m", "\x1b[36;20m"
	YELLOW, RED, BOLD_RED = "\x1b[33;20m", "\x1b[31;20m", "\x1b[31;1m"
	BLUE, BOLD_GREEN = "\x1b[34;20m", "\x1b[92m"
	WHITE = "\x1b[37;20m"
	RESET, DIM = "\x1b[0m", "\x1b[2m"

	LEVEL_COLORS = {
		logging.DEBUG: BLUE,
		logging.INFO: BOLD_GREEN,
		logging.WARNING: YELLOW,
		logging.ERROR: RED,
		logging.CRITICAL: BOLD_RED,
	}

	MESSAGE_COLORS = {
		logging.DEBUG: GREY,
		logging.INFO: CYAN,
		logging.WARNING: YELLOW,
		logging.ERROR: RED,
		logging.CRITICAL: BOLD_RED,
	}

	def __init__(self, use_colors: bool = True, show_path: bool = True):
		super().__init__()
		self.use_colors = use_colors
		self.show_path = show_path

	def format(self, record: logging.LogRecord) -> str:
		ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

		if self.show_path:
			try:
				# Tenta obter o caminho relativo ao diretório atual
				fp = Path(record.pathname).relative_to(Path.cwd())
			except ValueError:
				# Se não conseguir, usa o caminho absoluto
				fp = Path(record.pathname)
			location = f"{fp}:{record.lineno}"
		else:
			location = ""

		if self.use_colors:
			lc = self.LEVEL_COLORS.get(record.levelno, self.GREY)
			mc = self.MESSAGE_COLORS.get(record.levelno, self.RESET)
			ln = f"{lc}{record.levelname:8s}{self.RESET}"
			msg = f"{mc}{record.getMessage()}{self.RESET}"

			if self.show_path and location:
				return (
					f"[{self.WHITE}{ts}{self.RESET}] {ln} "
					f"[{self.WHITE}{location}{self.RESET}] {msg}"
				)
			else:
				return f"[{self.WHITE}{ts}{self.RESET}] {ln} {msg}"

		if self.show_path and location:
			return f"[{ts}] {record.levelname:8s} [{location}] {record.getMessage()}"
		else:
			return f"[{ts}] {record.levelname:8s} {record.getMessage()}"


class LoggerMeta(type):
	"""Singleton Metaclass"""

	_instances: dict = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super().__call__(*args, **kwargs)
		return cls._instances[cls]


class Logger(metaclass=LoggerMeta):
	"""Singleton Logger with Uvicorn style using metaclass (Python 3.13+)"""

	def __init__(
		self,
		name: str = "app",
		level: int = logging.INFO,
		use_colors: bool | None = None,
		show_path: bool = True,
		log_file: str | Path | None = None,
	):
		# Prevent reinitialization
		if hasattr(self, "_logger"):
			return

		self._logger = logging.getLogger(name)
		self._logger.setLevel(level)
		self._logger.handlers.clear()

		# Console handler
		if use_colors is None:
			use_colors = sys.stderr.isatty()

		console_handler = logging.StreamHandler(sys.stderr)
		console_handler.setLevel(level)
		console_handler.setFormatter(Formatter(use_colors, show_path))
		self._logger.addHandler(console_handler)

		if log_file:
			file_handler = logging.FileHandler(log_file, encoding="utf-8")
			file_handler.setLevel(level)
			file_handler.setFormatter(Formatter(use_colors=False, show_path=show_path))
			self._logger.addHandler(file_handler)

		self._logger.propagate = False

	def reconfigure(
		self,
		name: str = "app",
		level: int = logging.INFO,
		use_colors: bool | None = None,
		show_path: bool = True,
		log_file: str | Path | None = None,
	) -> Self:
		"""Reconfigures the existing logger"""
		self._logger = logging.getLogger(name)
		self._logger.setLevel(level)
		self._logger.handlers.clear()

		if use_colors is None:
			use_colors = sys.stderr.isatty()

		console_handler = logging.StreamHandler(sys.stderr)
		console_handler.setLevel(level)
		console_handler.setFormatter(Formatter(use_colors, show_path))
		self._logger.addHandler(console_handler)

		if log_file:
			file_handler = logging.FileHandler(log_file, encoding="utf-8")
			file_handler.setLevel(level)
			file_handler.setFormatter(Formatter(use_colors=False, show_path=show_path))
			self._logger.addHandler(file_handler)

		self._logger.propagate = False
		return self

	@classmethod
	def reset(cls) -> None:
		"""Resets the singleton (useful for testing)"""
		LoggerMeta._instances.pop(cls, None)

	def debug(self, msg: str, *args, **kwargs) -> None:
		self._logger.debug(msg, *args, stacklevel=2, **kwargs)

	def info(self, msg: str, *args, **kwargs) -> None:
		self._logger.info(msg, *args, stacklevel=2, **kwargs)

	def warning(self, msg: str, *args, **kwargs) -> None:
		self._logger.warning(msg, *args, stacklevel=2, **kwargs)

	def error(self, msg: str, *args, **kwargs) -> None:
		self._logger.error(msg, *args, stacklevel=2, **kwargs)

	def critical(self, msg: str, *args, **kwargs) -> None:
		self._logger.critical(msg, *args, stacklevel=2, **kwargs)

	def exception(self, msg: str, *args, **kwargs) -> None:
		self._logger.exception(msg, *args, stacklevel=2, **kwargs)

	def set_level(self, level: int) -> Self:
		self._logger.setLevel(level)
		for handler in self._logger.handlers:
			handler.setLevel(level)
		return self


logger: Logger = Logger(show_path=True)

# logger = Logger(show_path=True, log_file="app.log")  # Logs no console E arquivo
# logger.reconfigure(log_file="app.log")  # Adiciona arquivo depois
# logger.set_level(logging.DEBUG).debug("Debug enabled")
