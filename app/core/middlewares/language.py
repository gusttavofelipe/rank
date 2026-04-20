"""app/core/middlewares/language.py"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.i18n.manager import set_language


class LanguageMiddleware(BaseHTTPMiddleware):
	"""
	Middleware that checks the 'Accept-Language' header and sets the appropriate
	language for the response.
	"""

	async def dispatch(
		self, request: Request, call_next: RequestResponseEndpoint
	) -> Response:
		await set_language(request)
		response: Response = await call_next(request)
		return response
