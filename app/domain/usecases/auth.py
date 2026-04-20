"""app/domain/usecases/auth.py"""

import inspect
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions.auth import InvalidCredentialsError, TokenRevokedError
from app.core.exceptions.db import DBOperationError, ObjectAlreadyExistError
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
from app.infra.repositories.refresh_token import RefreshTokenRepositoryDependency
from app.infra.repositories.user import UserRepositoryDependency


class AuthUsecase:
	"""Handles authentication business logic."""

	def __init__(
		self,
		user_repository: UserRepositoryDependency,
		refresh_token_repository: RefreshTokenRepositoryDependency,
	) -> None:
		self.user_repository = user_repository
		self.refresh_token_repository = refresh_token_repository

	async def register(self, data: UserRegisterSchema) -> UserOutSchema:
		method_path = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			async with self.user_repository.transaction() as transaction:
				user = UserModel(
					**data.model_dump(exclude={"password"}),
					password_hash=hash_password(password=data.password),
					role=UserRoleEnum.REVIEWER,
				)
				await self.user_repository.create(orm_model=user, transaction=transaction)
				await transaction.flush()
				return UserOutSchema.model_validate(user)
		except IntegrityError:
			raise ObjectAlreadyExistError
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def login(self, data: UserLoginSchema) -> tuple[LoginOutSchema, str]:
		method_path = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			user = await self.user_repository.get(filters={"email": data.email})
			if not user or not verify_password(data.password, user.password_hash):
				raise InvalidCredentialsError

			if needs_rehash(user.password_hash):
				async with self.user_repository.transaction() as transaction:
					await self.user_repository.partial_update(
						filters={"pk_id": user.pk_id},
						data={"password_hash": hash_password(data.password)},
						transaction=transaction,
					)

			access_token = generate_access_token(
				user_id=str(user.id),
				role=user.role.value,
			)
			refresh_token_str, expires_at = generate_refresh_token()

			async with self.refresh_token_repository.transaction() as transaction:
				refresh_token = RefreshTokenModel(
					user_pk_id=user.pk_id,
					token=refresh_token_str,
					expires_at=expires_at,
				)
				await self.refresh_token_repository.create(
					orm_model=refresh_token,
					transaction=transaction,
				)

			result = LoginOutSchema(tokens=TokenOutSchema(access_token=access_token))
			return result, refresh_token_str  # refresh_token separado → vai pro cookie

		except (InvalidCredentialsError, DBOperationError):
			raise
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def refresh(self, refresh_token_str: str) -> tuple[TokenOutSchema, str]:
		method_path = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			refresh_token = await self.refresh_token_repository.get(
				filters={"token": refresh_token_str, "revoked": False}
			)
			if not refresh_token or refresh_token.expires_at.replace(
				tzinfo=UTC
			) < datetime.now(UTC):
				raise TokenRevokedError

			user = await self.user_repository.get(
				filters={"pk_id": refresh_token.user_pk_id}
			)
			if not user:
				raise InvalidCredentialsError

			new_access_token = generate_access_token(
				user_id=str(user.id),
				role=user.role.value,
			)
			new_refresh_token_str, expires_at = generate_refresh_token()

			async with self.refresh_token_repository.transaction() as transaction:
				await self.refresh_token_repository.revoke(
					refresh_token=refresh_token,
					transaction=transaction,
				)
				new_refresh_token = RefreshTokenModel(
					user_pk_id=user.pk_id,
					token=new_refresh_token_str,
					expires_at=expires_at,
				)
				await self.refresh_token_repository.create(
					orm_model=new_refresh_token,
					transaction=transaction,
				)

			return TokenOutSchema(access_token=new_access_token), new_refresh_token_str

		except (TokenRevokedError, InvalidCredentialsError):
			raise
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def logout(self, refresh_token_str: str) -> None:
		method_path = (
			f"{self.__class__.__module__}.{inspect.currentframe().f_code.co_qualname}"  # pyright: ignore
		)
		try:
			refresh_token = await self.refresh_token_repository.get(
				filters={"token": refresh_token_str}
			)
			if not refresh_token:
				return
			async with self.refresh_token_repository.transaction() as transaction:
				await self.refresh_token_repository.revoke(
					refresh_token=refresh_token,
					transaction=transaction,
				)
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)


AuthUsecaseDependency = Annotated[AuthUsecase, Depends()]
