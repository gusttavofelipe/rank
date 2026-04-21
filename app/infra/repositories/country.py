"""app/infra/repositories/user.py"""

from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import ColumnElement, Select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.dml import ReturningUpdate

from app.domain.models import CountryModel
from app.domain.schemas.country import CountryUpdateSchema
from app.infra.db.manager import DatabaseDependency
from app.infra.db.specifications.base import Specification
from app.infra.db.transaction import Transaction
from app.infra.repositories.postgres import PostgresRepository


class CountryRepository(PostgresRepository[CountryModel]):
	def __init__(self, session: DatabaseDependency) -> None:
		super().__init__(session=session)

	async def create(
		self, orm_model: CountryModel, transaction: Transaction[CountryModel]
	) -> CountryModel:
		return transaction.insert(orm_model=orm_model)

	async def get(
		self,
		spec: Specification[CountryModel],
		transaction: Transaction[CountryModel] | None = None,
	) -> CountryModel | None:
		session: AsyncSession = transaction.session if transaction else self.session
		query: Select[tuple[CountryModel]] = spec.apply(select(CountryModel))
		return (await session.execute(query)).scalars().first()

	async def partial_update(
		self,
		spec: Specification[CountryModel],
		data: CountryUpdateSchema,
		transaction: Transaction[CountryModel],
	) -> CountryModel | None:
		base_query: Select[tuple[CountryModel]] = spec.apply(select(CountryModel))
		update_data: dict[str, Any] = data.model_dump(mode="json", exclude_unset=True)

		if not update_data:
			return None

		clause: ColumnElement[bool] | None = base_query.whereclause
		if clause is None:
			return None

		stmt: ReturningUpdate[tuple[CountryModel]] = (
			update(CountryModel)
			.where(clause)
			.values(**update_data)
			.execution_options(synchronize_session=False)
			.returning(CountryModel)
		)
		result: Result[tuple[CountryModel]] = await transaction.session.execute(stmt)
		return result.scalars().first()

	async def list(
		self,
		spec: Specification[CountryModel],
		limit: int = 20,
		offset: int = 0,
	) -> list[CountryModel]:
		query: Select[tuple[CountryModel]] = (
			spec.apply(select(CountryModel)).limit(limit).offset(offset)
		)
		return list((await self.session.execute(query)).scalars().all())

	async def delete(
		self, orm_model: CountryModel, transaction: Transaction[CountryModel]
	) -> None:
		await transaction.delete(orm_model=orm_model)


CountryRepositoryDependency = Annotated[CountryRepository, Depends()]
