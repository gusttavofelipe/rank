"""app/infra/repositories/user.py"""

from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import ColumnElement, Select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.dml import Update

from app.domain.models import UserModel
from app.domain.schemas.user import UserUpdateSchema
from app.infra.db.manager import DatabaseDependency
from app.infra.db.specifications.base import Specification
from app.infra.db.transaction import Transaction
from app.infra.repositories.postgres import PostgresRepository


class UserRepository(PostgresRepository[UserModel]):
	def __init__(self, session: DatabaseDependency) -> None:
		super().__init__(session=session)

	async def create(
		self, orm_model: UserModel, transaction: Transaction[UserModel]
	) -> UserModel:
		return transaction.insert(orm_model=orm_model)

	async def get(
		self,
		spec: Specification[UserModel],
		transaction: Transaction[UserModel] | None = None,
	) -> UserModel | None:
		session: AsyncSession = transaction.session if transaction else self.session
		query: Select[tuple[UserModel]] = spec.apply(select(UserModel))
		return (await session.execute(query)).scalars().first()

	async def list(
		self,
		spec: Specification[UserModel],
		limit: int = 20,
		offset: int = 0,
	) -> list[UserModel]:
		query: Select[tuple[UserModel]] = (
			spec.apply(select(UserModel)).limit(limit).offset(offset)
		)
		return list((await self.session.execute(query)).scalars().all())

	async def partial_update(
		self,
		spec: Specification[UserModel],
		data: UserUpdateSchema,
		transaction: Transaction[UserModel],
	) -> UserModel | None:
		base_query: Select[tuple[UserModel]] = spec.apply(select(UserModel))
		update_data: dict[str, Any] = data.model_dump(mode="json", exclude_unset=True)

		if not update_data:
			return None

		clause: ColumnElement[bool] | None = base_query.whereclause
		if clause is None:
			return None

		stmt: Any = (
			update(UserModel)
			.where(clause)
			.values(**update_data)
			.execution_options(synchronize_session=False)
			.returning(UserModel)
		)
		result: Result[Any] = await transaction.session.execute(stmt)
		return result.scalars().first()

	async def update_password(
		self,
		spec: Specification[UserModel],
		password_hash: str,
		transaction: Transaction[UserModel],
	) -> None:
		base_query: Select[tuple[UserModel]] = spec.apply(select(UserModel))
		clause: ColumnElement[bool] | None = base_query.whereclause
		if clause is None:
			return

		stmt: Update = (
			update(UserModel)
			.where(clause)
			.values(password_hash=password_hash)
			.execution_options(synchronize_session=False)
		)
		await transaction.session.execute(stmt)

	async def delete(
		self, orm_model: UserModel, transaction: Transaction[UserModel]
	) -> None:
		await transaction.session.delete(orm_model)


UserRepositoryDependency = Annotated[UserRepository, Depends()]
