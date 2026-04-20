"""app/infra/repositories/refresh_token.py"""

from typing import Annotated, TypedDict

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.future import select

from app.domain.models.refresh_token import RefreshTokenModel
from app.infra.db.manager import DatabaseDependency
from app.infra.db.transaction import Transaction
from app.infra.repositories.postgres import PostgresRepository


class RefreshTokenFilters(TypedDict, total=False):
	token: str
	user_pk_id: int
	revoked: bool


class RefreshTokenRepository(PostgresRepository[RefreshTokenModel, RefreshTokenFilters]):
	def __init__(self, session: DatabaseDependency) -> None:
		super().__init__(session=session)

	async def create(
		self,
		orm_model: RefreshTokenModel,
		transaction: Transaction[RefreshTokenModel],
	) -> RefreshTokenModel:
		return transaction.insert(orm_model=orm_model)

	async def get(
		self,
		filters: RefreshTokenFilters,
		transaction: Transaction[RefreshTokenModel] | None = None,
	) -> RefreshTokenModel | None:
		session = transaction.session if transaction else self.session
		query = select(RefreshTokenModel)
		if token := filters.get("token"):
			query = query.where(RefreshTokenModel.token == token)
		if user_pk_id := filters.get("user_pk_id"):
			query = query.where(RefreshTokenModel.user_pk_id == user_pk_id)
		if (revoked := filters.get("revoked")) is not None:
			query = query.where(RefreshTokenModel.revoked == revoked)
		return (await session.execute(query)).scalars().first()

	async def revoke(
		self,
		refresh_token: RefreshTokenModel,
		transaction: Transaction[RefreshTokenModel],
	) -> None:
		refresh_token.revoked = True
		transaction.insert(orm_model=refresh_token)

	async def revoke_all(
		self,
		user_pk_id: int,
		transaction: Transaction[RefreshTokenModel],
	) -> None:
		stmt = (
			update(RefreshTokenModel)
			.where(RefreshTokenModel.user_pk_id == user_pk_id)
			.where(RefreshTokenModel.revoked == False)  # noqa: E712
			.values(revoked=True)
		)
		await transaction.session.execute(stmt)

	async def delete(
		self,
		orm_model: RefreshTokenModel,
		transaction: Transaction[RefreshTokenModel],
	) -> None:
		await transaction.session.delete(orm_model)


def get_refresh_token_repository(session: DatabaseDependency) -> RefreshTokenRepository:
	return RefreshTokenRepository(session=session)


RefreshTokenRepositoryDependency = Annotated[
	RefreshTokenRepository, Depends(get_refresh_token_repository)
]
