"""app/infra/db/specifications/refresh_token.py"""

from sqlalchemy import Select

from app.domain.models.refresh_token import RefreshTokenModel
from app.infra.db.specifications.base import Specification


class RefreshTokenByToken(Specification[RefreshTokenModel]):
	def __init__(self, token: str) -> None:
		self.token = token

	def apply(
		self, query: Select[tuple[RefreshTokenModel]]
	) -> Select[tuple[RefreshTokenModel]]:
		return query.where(RefreshTokenModel.token == self.token)


class RefreshTokenByUserPkId(Specification[RefreshTokenModel]):
	def __init__(self, user_pk_id: int) -> None:
		self.user_pk_id = user_pk_id

	def apply(
		self, query: Select[tuple[RefreshTokenModel]]
	) -> Select[tuple[RefreshTokenModel]]:
		return query.where(RefreshTokenModel.user_pk_id == self.user_pk_id)


class RefreshTokenNotRevoked(Specification[RefreshTokenModel]):
	def apply(
		self, query: Select[tuple[RefreshTokenModel]]
	) -> Select[tuple[RefreshTokenModel]]:
		return query.where(RefreshTokenModel.revoked == False)  # noqa: E712


class RefreshTokenRevoked(Specification[RefreshTokenModel]):
	def apply(
		self, query: Select[tuple[RefreshTokenModel]]
	) -> Select[tuple[RefreshTokenModel]]:
		return query.where(RefreshTokenModel.revoked == True)  # noqa: E712
