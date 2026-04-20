"""app/infra/repositories/user.py"""

import uuid
from typing import Annotated, TypedDict

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.future import select

from app.domain.models import UserModel
from app.domain.models.enums.user import UserRoleEnum
from app.infra.db.manager import DatabaseDependency
from app.infra.db.transaction import Transaction
from app.infra.repositories.postgres import PostgresRepository


class UserFilters(TypedDict, total=False):
	email: str
	role: UserRoleEnum
	is_verified: bool
	pk_id: int
	id: uuid.UUID


class UserUpdateData(TypedDict, total=False):
	name: str
	email: str
	password_hash: str
	profile_image_url: str | None
	role: UserRoleEnum
	is_verified: bool


class UserRepository(PostgresRepository[UserModel, UserFilters]):
	def __init__(self, session: DatabaseDependency) -> None:
		super().__init__(session=session)

	async def create(
		self, orm_model: UserModel, transaction: Transaction[UserModel]
	) -> UserModel:
		return transaction.insert(orm_model=orm_model)

	async def get(
		self,
		filters: UserFilters,
		transaction: Transaction[UserModel] | None = None,
	) -> UserModel | None:
		session = transaction.session if transaction else self.session
		query = select(UserModel)
		if email := filters.get("email"):
			query = query.where(UserModel.email == email)
		if role := filters.get("role"):
			query = query.where(UserModel.role == role)
		if (is_verified := filters.get("is_verified")) is not None:
			query = query.where(UserModel.is_verified == is_verified)
		if pk_id := filters.get("pk_id"):
			query = query.where(UserModel.pk_id == pk_id)
		return (await session.execute(query)).scalars().first()

	async def partial_update(
		self,
		filters: UserFilters,
		data: UserUpdateData,
		transaction: Transaction[UserModel],
	) -> UserModel | None:
		conditions = []
		if email := filters.get("email"):
			conditions.append(UserModel.email == email)
		if pk_id := filters.get("pk_id"):
			conditions.append(UserModel.pk_id == pk_id)

		stmt = (
			update(UserModel)
			.where(*conditions)
			.values(**data)
			.execution_options(synchronize_session=False)
			.returning(UserModel)
		)
		result = await transaction.session.execute(stmt)
		return result.scalars().first()

	async def delete(
		self, orm_model: UserModel, transaction: Transaction[UserModel]
	) -> None:
		await transaction.session.delete(orm_model)


UserRepositoryDependency = Annotated[UserRepository, Depends()]
