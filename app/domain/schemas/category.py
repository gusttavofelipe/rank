from pydantic import HttpUrl

from app.domain.schemas.base import BaseSchema, OutSchema


class CategoryCreateSchema(BaseSchema):
	name: str
	slug: str
	description: str
	icon: HttpUrl | None = None


class CategoryUpdateSchema(BaseSchema):
	name: str | None = None
	slug: str | None = None
	description: str | None = None
	icon: HttpUrl | None = None


class CategoryResponseSchema(CategoryCreateSchema, OutSchema): ...
