"""app/infra/db/specifications/user.py"""

import uuid

from sqlalchemy import Select

from app.domain.models.enums.user import UserRoleEnum
from app.domain.models.user import UserModel
from app.infra.db.specifications.base import Specification


class UserByEmail(Specification[UserModel]):
	def __init__(self, email: str) -> None:
		self.email = email

	def apply(self, query: Select[tuple[UserModel]]) -> Select[tuple[UserModel]]:
		return query.where(UserModel.email == self.email)


class UserByRole(Specification[UserModel]):
	def __init__(self, role: UserRoleEnum) -> None:
		self.role = role

	def apply(self, query: Select[tuple[UserModel]]) -> Select[tuple[UserModel]]:
		return query.where(UserModel.role == self.role)


class UserByIsVerified(Specification[UserModel]):
	def __init__(self, is_verified: bool) -> None:
		self.is_verified = is_verified

	def apply(self, query: Select[tuple[UserModel]]) -> Select[tuple[UserModel]]:
		return query.where(UserModel.is_verified == self.is_verified)


class UserByPkId(Specification[UserModel]):
	def __init__(self, pk_id: int) -> None:
		self.pk_id = pk_id

	def apply(self, query: Select[tuple[UserModel]]) -> Select[tuple[UserModel]]:
		return query.where(UserModel.pk_id == self.pk_id)


class UserById(Specification[UserModel]):
	def __init__(self, id: uuid.UUID) -> None:
		self.id = id

	def apply(self, query: Select[tuple[UserModel]]) -> Select[tuple[UserModel]]:
		return query.where(UserModel.id == self.id)
