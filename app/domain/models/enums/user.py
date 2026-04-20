"""app/domain/models/enums/user.py"""

from enum import StrEnum


class UserRoleEnum(StrEnum):
	REVIEWER = "reviewer"
	REVIEWED = "reviewed"
	ADMIN = "admin"
