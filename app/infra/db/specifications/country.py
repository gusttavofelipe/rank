"""app/infra/db/specifications/country.py"""

import uuid

from sqlalchemy import Select

from app.domain.models.country import CountryModel
from app.infra.db.specifications.base import Specification


class CountryByName(Specification[CountryModel]):
	def __init__(self, name: str) -> None:
		self.name: str = name

	def apply(self, query: Select[tuple[CountryModel]]) -> Select[tuple[CountryModel]]:
		return query.where(CountryModel.name.ilike(f"%{self.name}%"))


class CountryByCode(Specification[CountryModel]):
	def __init__(self, code: str) -> None:
		self.code: str = code

	def apply(self, query: Select[tuple[CountryModel]]) -> Select[tuple[CountryModel]]:
		return query.where(CountryModel.code == self.code)


class CountryById(Specification[CountryModel]):
	def __init__(self, id: uuid.UUID) -> None:
		self.id: uuid.UUID = id

	def apply(self, query: Select[tuple[CountryModel]]) -> Select[tuple[CountryModel]]:
		return query.where(CountryModel.id == self.id)
