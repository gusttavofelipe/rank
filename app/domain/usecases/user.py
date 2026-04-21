"""app/domain/usecases/user.py"""

import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions.db import DBOperationError, ObjectNotFound
from app.core.logging import get_logger
from app.domain.models import UserModel
from app.domain.schemas.user import UserOutSchema, UserUpdateSchema
from app.infra.db.specifications.user import UserById
from app.infra.repositories.user import UserRepositoryDependency

logger = get_logger(__name__)


class UserUsecase:
	"""Handles user business logic."""

	def __init__(self, user_repository: UserRepositoryDependency) -> None:
		self.user_repository: UserRepositoryDependency = user_repository

	async def partial_update(
		self, data: UserUpdateSchema, user_id: uuid.UUID
	) -> UserOutSchema:
		try:
			async with self.user_repository.transaction() as transaction:
				user: UserModel | None = await self.user_repository.partial_update(
					spec=UserById(id=user_id),
					data=data,
					transaction=transaction,
				)
				if user is not None:
					return UserOutSchema.model_validate(user)
			raise ObjectNotFound
		except IntegrityError as exc:
			logger.error(f"Integrity error: {exc}")
			raise DBOperationError
		except SQLAlchemyError as exc:
			logger.error(f"SQLAlchemy error in register: {exc}")
			raise DBOperationError


UserUsecaseDependency = Annotated[UserUsecase, Depends()]
