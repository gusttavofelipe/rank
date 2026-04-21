"""app/infra/repositories/user.py"""

from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import ColumnElement, Select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.dml import ReturningUpdate

from app.domain.models import CategoryModel
from app.domain.schemas.category import CategoryUpdateSchema
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

	async def partial_update(
		self,
		spec: Specification[CategoryModel],
		data: CategoryUpdateSchema,
		transaction: Transaction[CategoryModel],
	) -> CategoryModel | None:
		base_query: Select[tuple[CategoryModel]] = spec.apply(select(CategoryModel))
		update_data: dict[str, Any] = data.model_dump(mode="json", exclude_unset=True)

		if not update_data:
			return None

		clause: ColumnElement[bool] | None = base_query.whereclause
		if clause is None:
			return None

		stmt: ReturningUpdate[tuple[CategoryModel]] = (
			update(CategoryModel)
			.where(clause)
			.values(**update_data)
			.execution_options(synchronize_session=False)
			.returning(CategoryModel)
		)
		result: Result[tuple[CategoryModel]] = await transaction.session.execute(stmt)
		return result.scalars().first()

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
