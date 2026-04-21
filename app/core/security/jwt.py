"""app/core/security/jwt.py"""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import settings

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
REFRESH_TOKEN_EXPIRE_DAYS: int = 30


def generate_access_token(user_id: str, role: str) -> str:
	expire: datetime = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	return jwt.encode(
		{"sub": user_id, "role": role, "exp": expire, "type": "access"},
		settings.SECRET_KEY,
		algorithm=ALGORITHM,
	)


def generate_refresh_token() -> tuple[str, datetime]:
	expire: datetime = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
	token: str = secrets.token_hex(64)
	return token, expire


def decode_access_token(token: str) -> dict[str, Any]:
	try:
		payload: dict[str, Any] = jwt.decode(
			token, settings.SECRET_KEY, algorithms=[ALGORITHM]
		)
		if payload.get("type") != "access":
			raise JWTError("Invalid token type")
		return payload
	except ExpiredSignatureError:
		raise
	except JWTError:
		raise
