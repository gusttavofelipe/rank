"""app/core/exceptions/auth.py"""

from app.core.exceptions.base import CustomBaseException
from app.core.i18n.manager import _


class InvalidCredentialsError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message: str = message or _("Invalid credentials")
		super().__init__(*args, self.message)


class TokenRevokedError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message: str = message or _("Token has been revoked or expired")
		super().__init__(*args, self.message)


class TokenInvalidError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message: str = message or _("Invalid token")
		super().__init__(*args, self.message)


class UnauthorizedError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message: str = message or _("Unauthorized")
		super().__init__(*args, self.message)


class ForbiddenError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message: str = message or _("Forbidden")
		super().__init__(*args, self.message)
