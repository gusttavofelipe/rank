from typing import Self

from fastapi import Request
from pydantic import AnyHttpUrl, BaseModel, Field, NonNegativeInt

from app.domain.schemas.base import BaseSchema
from app.domain.schemas.query_params import BaseQueryParams


class CollectionResponse[SchemaT: BaseSchema](BaseModel):
	"""Schema for a paginated collection response.
	Represents a collection of items with pagination metadata.
	"""

	count: NonNegativeInt = Field(description="Total number of items across all pages")
	next: AnyHttpUrl = Field(description="URL for the next page of results")
	previous: AnyHttpUrl = Field(description="URL for the previous page of results")
	results: list[SchemaT] = Field(description="list of items for the current page")

	@classmethod
	def parse_collection(
		cls,
		request: Request,
		results: list[SchemaT],
		query_params: BaseQueryParams,
		count: int,
	) -> Self:
		"""Parses data and request information to create a CollectionResponse instance.

		Args:
		    request (Request):
		        The incoming request object, used to build pagination URLs.
		    results (list[SchemaT]):
		        The list of items for the current page, expected to be Pydantic schemas.
		    query_params (BaseQueryParams):
		        The query parameters used for pagination (offset and limit).
		    count (int): The total number of items in the collection across all pages.

		Returns:
		    CollectionResponse[SchemaT]:
		        A CollectionResponse instance populated with pagination
		        metadata and the current page's results.
		"""
		previous_calc: int = query_params.offset - query_params.limit
		previous_offset: int = previous_calc if previous_calc > 0 else 0
		next_offset: int = query_params.offset + query_params.limit

		collection_response: dict[str, int | list[SchemaT] | str] = {
			"count": count,
			"next": str(request.url.include_query_params(offset=next_offset)),
			"previous": str(request.url.include_query_params(offset=previous_offset)),
			"results": results,
		}

		return cls.model_validate(collection_response)


# IMPLEMENTAR: Keyset/Cursor
