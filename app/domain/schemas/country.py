from app.domain.schemas.base import BaseSchema, OutSchema


class CountryCreateSchema(BaseSchema):
	name: str
	code: str


class CountryUpdateSchema(BaseSchema):
	name: str | None = None
	code: str | None = None


class CountryResponseSchema(CountryCreateSchema, OutSchema): ...
