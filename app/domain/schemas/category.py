from pydantic import HttpUrl

from app.domain.schemas.base import BaseSchema, OutSchema


class CategoryCreateSchema(BaseSchema):
	name: str
	slug: str
	description: str
	icon: HttpUrl


class CategoryResponseSchema(CategoryCreateSchema, OutSchema): ...
