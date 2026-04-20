from pydantic import BaseModel, NonNegativeInt


class BaseQueryParams(BaseModel):
	"""Schema for standard pagination query parameters."""

	offset: NonNegativeInt = 0
	limit: NonNegativeInt = 10
	# order_by: Literal["created_at", "updated_at"] = "created_at"
