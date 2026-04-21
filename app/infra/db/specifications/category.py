"""app/infra/db/specifications/category.py"""

import uuid

from sqlalchemy import Select

from app.domain.models.category import CategoryModel
from app.infra.db.specifications.base import Specification


class CategoryByName(Specification[CategoryModel]):
	def __init__(self, name: str) -> None:
		self.name = name

	def apply(self, query: Select[tuple[CategoryModel]]) -> Select[tuple[CategoryModel]]:
		return query.where(CategoryModel.name.ilike(f"%{self.name}%"))


class CategoryBySlug(Specification[CategoryModel]):
	def __init__(self, slug: str) -> None:
		self.slug = slug

	def apply(self, query: Select[tuple[CategoryModel]]) -> Select[tuple[CategoryModel]]:
		return query.where(CategoryModel.slug == self.slug)


class CategoryById(Specification[CategoryModel]):
	def __init__(self, id: uuid.UUID) -> None:
		self.id = id

	def apply(self, query: Select[tuple[CategoryModel]]) -> Select[tuple[CategoryModel]]:
		return query.where(CategoryModel.id == self.id)
