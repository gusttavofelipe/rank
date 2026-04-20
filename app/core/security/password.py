"""app/core/security/password.py"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher(
	time_cost=3,  # iterações
	memory_cost=65536,  # 64MB
	parallelism=4,  # threads
	hash_len=32,
	salt_len=16,
)


def hash_password(password: str) -> str:
	peppered = password + settings.PASSWORD_PEPPER
	return _hasher.hash(peppered)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	peppered = plain_password + settings.PASSWORD_PEPPER
	try:
		return _hasher.verify(hashed_password, peppered)
	except (VerifyMismatchError, VerificationError, InvalidHashError):
		return False


def needs_rehash(hashed_password: str) -> bool:
	return _hasher.check_needs_rehash(hashed_password)
