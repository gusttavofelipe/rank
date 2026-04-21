"""app/infra/repositories/refresh_token.py"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.future import select

from app.domain.models.refresh_token import RefreshTokenModel
from app.infra.db.manager import DatabaseDependency
from app.infra.db.specifications.base import Specification
from app.infra.db.specifications.refresh_token import (
	RefreshTokenByUserPkId,
	RefreshTokenNotRevoked,
)
from app.infra.db.transaction import Transaction
from app.infra.repositories.postgres import PostgresRepository


class RefreshTokenRepository(PostgresRepository[RefreshTokenModel]):
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
		spec: Specification[RefreshTokenModel],
		transaction: Transaction[RefreshTokenModel] | None = None,
	) -> RefreshTokenModel | None:
		session = transaction.session if transaction else self.session
		query = spec.apply(select(RefreshTokenModel))
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
		base_query = (
			RefreshTokenByUserPkId(user_pk_id) & RefreshTokenNotRevoked()
		).apply(select(RefreshTokenModel))

		clause = base_query.whereclause
		if clause is None:
			return

		stmt = update(RefreshTokenModel).where(clause).values(revoked=True)
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
