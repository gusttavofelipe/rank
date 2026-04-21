"""app/core/exceptions/base.py"""


class CustomBaseException(Exception):
	def __init__(self, *args: object, message: str | None = None) -> None:
		super().__init__(*args)

		if message:
			self.message: str = message
