"""app/domain/usecases/country.py"""

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
from app.domain.models import CountryModel
from app.domain.schemas.country import (
	CountryCreateSchema,
	CountryResponseSchema,
	CountryUpdateSchema,
)
from app.infra.db.specifications.base import Specification
from app.infra.db.specifications.country import CountryByCode, CountryById, CountryByName
from app.infra.repositories.country import CountryRepositoryDependency

logger = get_logger(__name__)


class CountryUsecase:
	"""Handles country business logic."""

	def __init__(self, country_repository: CountryRepositoryDependency) -> None:
		self.country_repository: CountryRepositoryDependency = country_repository

	async def create(self, data: CountryCreateSchema) -> CountryResponseSchema:
		try:
			async with self.country_repository.transaction() as transaction:
				country: CountryModel = CountryModel(**data.model_dump(mode="json"))
				await self.country_repository.create(
					orm_model=country, transaction=transaction
				)
				await transaction.flush()
				return CountryResponseSchema.model_validate(country)
		except IntegrityError:
			raise ObjectAlreadyExistError
		except SQLAlchemyError:
			raise DBOperationError

	async def partial_update(
		self, data: CountryUpdateSchema, id: uuid.UUID
	) -> CountryResponseSchema:
		try:
			async with self.country_repository.transaction() as transaction:
				country: (
					CountryModel | None
				) = await self.country_repository.partial_update(
					spec=CountryById(id=id),
					data=data,
					transaction=transaction,
				)
				if country is not None:
					return CountryResponseSchema.model_validate(country)
			raise ObjectNotFound
		except IntegrityError as exc:
			logger.error(f"Integrity error: {exc}")
			raise DBOperationError
		except SQLAlchemyError as exc:
			logger.error(f"SQLAlchemy error: {exc}")
			raise DBOperationError

	async def get_by_id(self, id: uuid.UUID) -> CountryResponseSchema:
		try:
			country: CountryModel | None = await self.country_repository.get(
				CountryById(id)
			)
			if not country:
				raise ObjectNotFound
			return CountryResponseSchema.model_validate(country)
		except ObjectNotFound:
			raise
		except SQLAlchemyError:
			raise DBOperationError

	async def get_by_code(self, code: str) -> CountryResponseSchema:
		try:
			country: CountryModel | None = await self.country_repository.get(
				CountryByCode(code=code)
			)
			if not country:
				raise ObjectNotFound
			return CountryResponseSchema.model_validate(country)
		except ObjectNotFound:
			raise
		except SQLAlchemyError:
			raise DBOperationError

	async def list(self, name: str | None = None) -> list[CountryResponseSchema]:
		try:
			spec: Specification[CountryModel] = (
				CountryByName(name) if name else CountryByName("")
			)
			countries: list[CountryModel] = await self.country_repository.list_(spec)
			return [CountryResponseSchema.model_validate(c) for c in countries]
		except SQLAlchemyError:
			raise DBOperationError


CountryUsecaseDependency = Annotated[CountryUsecase, Depends()]
