"""app/domain/usecases/category.py"""

import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions.db import (
	DBOperationError,
	ObjectAlreadyExistError,
	ObjectNotFound,
)
from app.core.logging import get_logger
from app.domain.models import CategoryModel
from app.domain.schemas.category import (
	CategoryCreateSchema,
	CategoryResponseSchema,
	CategoryUpdateSchema,
)
from app.infra.db.specifications.category import CategoryById, CategoryBySlug
from app.infra.repositories.category import CategoryRepositoryDependency

logger = get_logger(__name__)


class CategoryUsecase:
	"""Handles category business logic."""

	def __init__(self, category_repository: CategoryRepositoryDependency) -> None:
		self.category_repository: CategoryRepositoryDependency = category_repository

	async def create(self, data: CategoryCreateSchema) -> CategoryResponseSchema:
		try:
			async with self.category_repository.transaction() as transaction:
				category: CategoryModel = CategoryModel(**data.model_dump(mode="json"))
				await self.category_repository.create(
					orm_model=category, transaction=transaction
				)
				await transaction.flush()
				return CategoryResponseSchema.model_validate(category)
		except IntegrityError as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise ObjectAlreadyExistError
		except SQLAlchemyError as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise DBOperationError

	async def partial_update(
		self, data: CategoryUpdateSchema, id: uuid.UUID
	) -> CategoryResponseSchema:
		try:
			async with self.category_repository.transaction() as transaction:
				category: (
					CategoryModel | None
				) = await self.category_repository.partial_update(
					spec=CategoryById(id=id),
					data=data,
					transaction=transaction,
				)
				if category is not None:
					return CategoryResponseSchema.model_validate(category)
			raise ObjectNotFound
		except IntegrityError as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise DBOperationError
		except SQLAlchemyError as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise DBOperationError

	async def get_by_id(self, id: uuid.UUID) -> CategoryResponseSchema:
		try:
			category: CategoryModel | None = await self.category_repository.get(
				CategoryById(id)
			)
			if not category:
				raise ObjectNotFound
			return CategoryResponseSchema.model_validate(category)
		except ObjectNotFound as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise
		except SQLAlchemyError as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise DBOperationError

	async def get_by_slug(self, slug: str) -> CategoryResponseSchema:
		try:
			category: CategoryModel | None = await self.category_repository.get(
				CategoryBySlug(slug)
			)
			if not category:
				raise ObjectNotFound
			return CategoryResponseSchema.model_validate(category)
		except ObjectNotFound as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise
		except SQLAlchemyError as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise DBOperationError

	async def list(self, name: str | None = None) -> list[CategoryResponseSchema]:
		try:
			from app.infra.db.specifications.base import Specification
			from app.infra.db.specifications.category import CategoryByName

			spec: Specification[CategoryModel] = (
				CategoryByName(name) if name else CategoryByName("")
			)
			categories: list[CategoryModel] = await self.category_repository.list_(spec)
			return [CategoryResponseSchema.model_validate(c) for c in categories]
		except SQLAlchemyError as exc:
			logger.error(f"{exc.__class__.__name__} error: {exc}")
			raise DBOperationError


CategoryUsecaseDependency = Annotated[CategoryUsecase, Depends()]
