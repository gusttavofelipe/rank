"""app/core/logging/_context.py

Thread-safe, async-safe log context via Python's contextvars.

Each asyncio task or OS thread gets its own isolated copy of the context,
so concurrent requests never bleed fields into each other.

Typical usage in a FastAPI middleware:

    token = bind(request_id="abc-123", user_id="usr-42")
    try:
        response = await call_next(request)
    finally:
        unbind(token)

Or with the scoped helper:

    with bound_context(request_id="abc-123"):
        logger.info("handling request")   # context included automatically
"""

import contextvars
from collections.abc import Generator
from contextlib import contextmanager

__all__ = [
	"ContextData",
	"bind",
	"unbind",
	"get_context",
	"bound_context",
]

type ContextData = dict[str, str | int | bool | None]

_log_context: contextvars.ContextVar[ContextData] = contextvars.ContextVar(
	"log_context",
	default={},
)


def bind(**fields: str | int | bool | None) -> contextvars.Token[ContextData]:
	"""
	Add fields to the current log context.

	Merges *fields* on top of whatever was already bound, so successive calls
	are additive.  Returns a token that can be passed to unbind() to restore
	the previous state — important for middleware that must clean up after the
	request.

	Args:
	    **fields: Arbitrary key/value pairs (request_id, user_id, trace_id…).

	Returns:
	    A contextvars.Token — pass it to unbind() when done.

	Example:
	    token = bind(request_id="abc", user_id="123")
	    # ... handle request ...
	    unbind(token)
	"""
	current: ContextData = _log_context.get()
	return _log_context.set({**current, **fields})


def unbind(token: contextvars.Token[ContextData]) -> None:
	"""
	Restore the context to the state captured by the matching bind() call.

	Args:
	    token: The token returned by the corresponding bind() call.
	"""
	_log_context.reset(token)


def get_context() -> ContextData:
	"""
	Return a shallow copy of the current log context.

	Callers receive a snapshot — mutating the returned dict has no effect on
	the live context.
	"""
	return dict(_log_context.get())


@contextmanager
def bound_context(**fields: str | int | bool | None) -> Generator[None]:
	"""
	Context manager that binds fields and automatically unbinds on exit,
	even if an exception is raised inside the block.

	Args:
	    **fields: Same key/value pairs accepted by bind().

	Example:
	    with bound_context(request_id="abc-123", user_id="usr-42"):
	        logger.info("fetching user")   # context fields appear in every log
	"""
	token: contextvars.Token[ContextData] = bind(**fields)
	try:
		yield
	finally:
		unbind(token)
