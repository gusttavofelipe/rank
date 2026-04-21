"""app/core/i18n/manager.py"""

from gettext import NullTranslations, translation
from pathlib import Path

from fastapi import Request


class TranslationManager:
	"""
	Singleton that manages translations at runtime.
	"""

	__instance: "TranslationManager | None" = None
	translations: NullTranslations | None

	def __new__(cls) -> "TranslationManager":
		if cls.__instance is None:
			cls.__instance = super().__new__(cls)
			cls.__instance.translations = None
			cls.__instance.setup_translation(lang="en")
		return cls.__instance

	def setup_translation(self, lang: str) -> None:
		"""Set up translations for a given language."""
		locales_dir: Path = Path(__file__).parent / "locales"
		self.translations = translation(
			"messages", localedir=locales_dir, languages=[lang], fallback=True
		)

	def translate(self, text: str) -> str:
		"""Return the translated string."""
		if not self.translations:
			self.setup_translation("en")
		return self.translations.gettext(text)  # type: ignore[union-attr]


async def set_language(request: Request) -> None:
	"""Middleware helper to set language based on the Accept-Language header."""
	translator: TranslationManager = TranslationManager()
	lang: str = (request.headers.get("Accept-Language") or "en").replace("-", "_")
	translator.setup_translation(lang)


def _(text: str) -> str:
	"""Shortcut to get translated text."""
	return TranslationManager().translate(text)
