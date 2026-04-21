"""app/infra/repositories/user.py"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.future import select

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
		session = transaction.session if transaction else self.session
		query = spec.apply(select(UserModel))
		return (await session.execute(query)).scalars().first()

	async def list(
		self,
		spec: Specification[UserModel],
		limit: int = 20,
		offset: int = 0,
	) -> list[UserModel]:
		query = spec.apply(select(UserModel)).limit(limit).offset(offset)
		return list((await self.session.execute(query)).scalars().all())

	async def partial_update(
		self,
		spec: Specification[UserModel],
		data: UserUpdateSchema,
		transaction: Transaction[UserModel],
	) -> UserModel | None:
		base_query = spec.apply(select(UserModel))
		update_data = data.model_dump(exclude_unset=True)

		if not update_data:
			return None

		clause = base_query.whereclause
		if clause is None:
			return None

		stmt = (
			update(UserModel)
			.where(clause)
			.values(**update_data)
			.execution_options(synchronize_session=False)
			.returning(UserModel)
		)
		result = await transaction.session.execute(stmt)
		return result.scalars().first()

	async def update_password(
		self,
		spec: Specification[UserModel],
		password_hash: str,
		transaction: Transaction[UserModel],
	) -> None:
		base_query = spec.apply(select(UserModel))
		clause = base_query.whereclause
		if clause is None:
			return

		stmt = (
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
