# app/domain/usecases/category.py
import inspect
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions.db import (
	DBOperationError,
	ObjectAlreadyExistError,
	ObjectNotFound,
)
from app.domain.models import CategoryModel
from app.domain.schemas.category import CategoryCreateSchema, CategoryResponseSchema
from app.infra.db.specifications.category import CategoryById, CategoryBySlug
from app.infra.repositories.category import CategoryRepositoryDependency


class CategoryUsecase:
	"""Handles category business logic."""

	def __init__(self, category_repository: CategoryRepositoryDependency) -> None:
		self.category_repository: CategoryRepositoryDependency = category_repository

	async def create(self, data: CategoryCreateSchema) -> CategoryResponseSchema:
		method_path: str = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			async with self.category_repository.transaction() as transaction:
				category: CategoryModel = CategoryModel(**data.model_dump(mode="json"))
				await self.category_repository.create(
					orm_model=category, transaction=transaction
				)
				await transaction.flush()
				return CategoryResponseSchema.model_validate(category)
		except IntegrityError:
			raise ObjectAlreadyExistError
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def get_by_id(self, id: uuid.UUID) -> CategoryResponseSchema:
		method_path: str = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			category: CategoryModel | None = await self.category_repository.get(
				CategoryById(id)
			)
			if not category:
				raise ObjectNotFound
			return CategoryResponseSchema.model_validate(category)
		except ObjectNotFound:
			raise
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def get_by_slug(self, slug: str) -> CategoryResponseSchema:
		method_path: str = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			category: CategoryModel | None = await self.category_repository.get(
				CategoryBySlug(slug)
			)
			if not category:
				raise ObjectNotFound
			return CategoryResponseSchema.model_validate(category)
		except ObjectNotFound:
			raise
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def list(self, name: str | None = None) -> list[CategoryResponseSchema]:
		method_path: str = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			from app.infra.db.specifications.base import Specification
			from app.infra.db.specifications.category import CategoryByName

			spec: Specification[CategoryModel] = (
				CategoryByName(name) if name else CategoryByName("")
			)
			categories: list[CategoryModel] = await self.category_repository.list_(spec)
			return [CategoryResponseSchema.model_validate(c) for c in categories]
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)


CategoryUsecaseDependency = Annotated[CategoryUsecase, Depends()]
