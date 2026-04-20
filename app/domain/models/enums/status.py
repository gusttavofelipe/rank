"""app/domain/models/enums/status.py"""

from enum import StrEnum


class StatusEnum(StrEnum):
	PENDING = "pending"
	APPROVED = "approved"
	REJECTED = "rejected"
