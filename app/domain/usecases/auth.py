"""app/domain/usecases/auth.py"""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions.auth import InvalidCredentialsError, TokenRevokedError
from app.core.exceptions.db import DBOperationError, ObjectAlreadyExistError
from app.core.logging import get_logger
from app.core.security.jwt import generate_access_token, generate_refresh_token
from app.core.security.password import hash_password, needs_rehash, verify_password
from app.domain.models.enums.user import UserRoleEnum
from app.domain.models.refresh_token import RefreshTokenModel
from app.domain.models.user import UserModel
from app.domain.schemas.auth import (
	LoginOutSchema,
	TokenOutSchema,
	UserLoginSchema,
	UserRegisterSchema,
)
from app.domain.schemas.user import UserOutSchema
from app.infra.db.specifications.refresh_token import (
	RefreshTokenByToken,
	RefreshTokenNotRevoked,
)
from app.infra.db.specifications.user import UserByEmail, UserByPkId
from app.infra.repositories.refresh_token import RefreshTokenRepositoryDependency
from app.infra.repositories.user import UserRepositoryDependency

logger = get_logger(__name__)


class AuthUsecase:
	"""Handles authentication business logic."""

	def __init__(
		self,
		user_repository: UserRepositoryDependency,
		refresh_token_repository: RefreshTokenRepositoryDependency,
	) -> None:
		self.user_repository: UserRepositoryDependency = user_repository
		self.refresh_token_repository: RefreshTokenRepositoryDependency = (
			refresh_token_repository
		)

	async def register(self, data: UserRegisterSchema) -> UserOutSchema:
		try:
			async with self.user_repository.transaction() as transaction:
				user: UserModel = UserModel(
					**data.model_dump(mode="json", exclude={"password"}),
					password_hash=hash_password(password=data.password),
					role=UserRoleEnum.REVIEWER,
				)
				await self.user_repository.create(orm_model=user, transaction=transaction)
				await transaction.flush()
				return UserOutSchema.model_validate(user)
		except IntegrityError as exc:
			logger.error(f"IntegrityError in register: {exc}")
			raise ObjectAlreadyExistError
		except SQLAlchemyError as exc:
			logger.error(f"SQLAlchemy error in register: {exc}")
			raise DBOperationError

	async def login(self, data: UserLoginSchema) -> tuple[LoginOutSchema, str]:
		try:
			user: UserModel | None = await self.user_repository.get(
				UserByEmail(data.email)
			)
			if not user or not verify_password(data.password, user.password_hash):
				raise InvalidCredentialsError

			if needs_rehash(user.password_hash):
				async with self.user_repository.transaction() as transaction:
					await self.user_repository.update_password(
						spec=UserByPkId(user.pk_id),
						password_hash=hash_password(data.password),
						transaction=transaction,
					)

			access_token: str = generate_access_token(
				user_id=str(user.id), role=user.role.value
			)
			refresh_token_str: str
			expires_at: datetime
			refresh_token_str, expires_at = generate_refresh_token()

			async with self.refresh_token_repository.transaction() as transaction:
				await self.refresh_token_repository.create(
					orm_model=RefreshTokenModel(
						user_pk_id=user.pk_id,
						token=refresh_token_str,
						expires_at=expires_at,
					),
					transaction=transaction,
				)

			return LoginOutSchema(
				tokens=TokenOutSchema(access_token=access_token)
			), refresh_token_str

		except (InvalidCredentialsError, DBOperationError):
			raise
		except SQLAlchemyError as exc:
			logger.error(f"SQLAlchemy error in login: {exc}")
			raise DBOperationError

	async def refresh(self, refresh_token_str: str) -> tuple[TokenOutSchema, str]:
		try:
			refresh_token: (
				RefreshTokenModel | None
			) = await self.refresh_token_repository.get(
				RefreshTokenByToken(refresh_token_str) & RefreshTokenNotRevoked()
			)
			if not refresh_token or refresh_token.expires_at.replace(
				tzinfo=UTC
			) < datetime.now(UTC):
				raise TokenRevokedError

			user: UserModel | None = await self.user_repository.get(
				UserByPkId(refresh_token.user_pk_id)
			)
			if not user:
				raise InvalidCredentialsError

			new_access_token: str = generate_access_token(
				user_id=str(user.id), role=user.role.value
			)
			new_refresh_token_str: str
			expires_at: datetime
			new_refresh_token_str, expires_at = generate_refresh_token()

			async with self.refresh_token_repository.transaction() as transaction:
				await self.refresh_token_repository.revoke(
					refresh_token=refresh_token,
					transaction=transaction,
				)
				await self.refresh_token_repository.create(
					orm_model=RefreshTokenModel(
						user_pk_id=user.pk_id,
						token=new_refresh_token_str,
						expires_at=expires_at,
					),
					transaction=transaction,
				)

			return TokenOutSchema(access_token=new_access_token), new_refresh_token_str

		except (TokenRevokedError, InvalidCredentialsError):
			raise
		except SQLAlchemyError as exc:
			logger.error(f"SQLAlchemy error in refresh: {exc}")
			raise DBOperationError

	async def logout(self, refresh_token_str: str) -> None:
		try:
			refresh_token: (
				RefreshTokenModel | None
			) = await self.refresh_token_repository.get(
				RefreshTokenByToken(refresh_token_str)
			)
			if not refresh_token:
				return
			async with self.refresh_token_repository.transaction() as transaction:
				await self.refresh_token_repository.revoke(
					refresh_token=refresh_token,
					transaction=transaction,
				)
		except SQLAlchemyError as exc:
			logger.error(f"SQLAlchemy error in logout: {exc}")
			raise DBOperationError

	async def me(self, user: UserModel) -> UserOutSchema:
		return UserOutSchema.model_validate(user)


AuthUsecaseDependency = Annotated[AuthUsecase, Depends()]
