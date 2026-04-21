"""app/infra/repositories/user.py"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.models import CategoryModel
from app.infra.db.manager import DatabaseDependency
from app.infra.db.specifications.base import Specification
from app.infra.db.transaction import Transaction
from app.infra.repositories.postgres import PostgresRepository


class CategoryRepository(PostgresRepository[CategoryModel]):
	def __init__(self, session: DatabaseDependency) -> None:
		super().__init__(session=session)

	async def create(
		self, orm_model: CategoryModel, transaction: Transaction[CategoryModel]
	) -> CategoryModel:
		return transaction.insert(orm_model=orm_model)

	async def get(
		self,
		spec: Specification[CategoryModel],
		transaction: Transaction[CategoryModel] | None = None,
	) -> CategoryModel | None:
		session: AsyncSession = transaction.session if transaction else self.session
		query: Select[tuple[CategoryModel]] = spec.apply(select(CategoryModel))
		return (await session.execute(query)).scalars().first()

	async def list_(
		self,
		spec: Specification[CategoryModel],
		limit: int = 20,
		offset: int = 0,
	) -> list[CategoryModel]:
		query: Select[tuple[CategoryModel]] = (
			spec.apply(select(CategoryModel)).limit(limit).offset(offset)
		)
		return list((await self.session.execute(query)).scalars().all())

	async def delete(
		self, orm_model: CategoryModel, transaction: Transaction[CategoryModel]
	) -> None:
		await transaction.delete(orm_model=orm_model)


CategoryRepositoryDependency = Annotated[CategoryRepository, Depends()]
