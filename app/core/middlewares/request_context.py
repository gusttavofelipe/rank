"""app/core/middlewares/request_context.py

Middleware that generates a unique request_id for every incoming HTTP request
and binds it to the log context for the lifetime of that request.

Every log line emitted during request handling will automatically include
the request_id field, making it trivial to correlate logs across services
in Datadog, Loki, ELK, or any structured log ingestor.

The request_id is also forwarded in the response header (X-Request-ID) so
clients and upstream services can reference it in bug reports.

Usage — register in main.py:
    app.add_middleware(RequestContextMiddleware)

If the incoming request already carries an X-Request-ID header (set by an
API gateway or load balancer), that value is reused instead of generating a
new one, preserving distributed trace chains.
"""

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import bound_context, get_logger

__all__ = ["RequestContextMiddleware"]

_REQUEST_ID_HEADER: str = "X-Request-ID"

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
	"""
	Injects a request_id into the log context for every HTTP request.

	Behaviour:
	  - Reads X-Request-ID from the incoming headers.  If absent, generates a
	    new UUID4.
	  - Binds request_id (and optionally the HTTP method + path) to the log
	    context via contextvars so all log lines within the same asyncio task
	    carry those fields automatically.
	  - Writes X-Request-ID back into the response headers.
	  - Cleans up the context automatically when the response is sent,
	    regardless of exceptions.
	"""

	async def dispatch(
		self,
		request: Request,
		call_next: Callable[[Request], Awaitable[Response]],
	) -> Response:
		request_id: str = request.headers.get(_REQUEST_ID_HEADER) or str(uuid.uuid4())

		with bound_context(
			request_id=request_id,
			method=request.method,
			path=request.url.path,
		):
			logger.debug(f"Request started — {request.method} {request.url.path}")
			response: Response = await call_next(request)
			response.headers[_REQUEST_ID_HEADER] = request_id
			logger.debug(
				f"Request finished — {request.method} {request.url.path}"
				f" → {response.status_code}"
			)

		return response
