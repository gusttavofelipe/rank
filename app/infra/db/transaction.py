"""app/infra/db/transaction.py"""

from collections.abc import Sequence
from types import TracebackType
from typing import Self

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.domain.models.base import DeclarativeBaseModel

logger = get_logger(__name__)


class Transaction[OrmModelT: DeclarativeBaseModel]:
	"""Transaction manager with automatic commit/rollback."""

	__slots__ = ("session",)

	def __init__(self, session: AsyncSession) -> None:
		self.session = session

	async def __aenter__(self) -> Self:
		"""Marks that this context should manage the transaction."""
		# SQLAlchemy AsyncSession automatically starts a transaction
		# on the first database operation. No need to call begin() manually.
		logger.debug("Transaction started")
		return self

	async def __aexit__(
		self,
		exc_t: type[BaseException] | None,
		exc_v: BaseException | None,
		exc_tb: TracebackType | None,
	) -> None:
		"""Finalizes the transaction, committing or rolling back changes."""

		try:
			if exc_v and exc_t:
				error: str = f"[{exc_t.__name__}]: {exc_v}"
				logger.error(f"Exception in transaction, rolling back - {error}")
				await self.session.rollback()
			else:
				await self.session.commit()
				logger.debug("Transaction committed")

		except SQLAlchemyError as exc:
			logger.error(f"Error during commit/rollback: {exc}")
			await self.session.rollback()
			raise

	def insert(self, orm_model: OrmModelT) -> OrmModelT:
		"""Adds an ORM model to the session for insertion."""
		self.session.add(instance=orm_model)
		return orm_model

	def insert_all(self, orm_models: Sequence[OrmModelT]) -> Sequence[OrmModelT]:
		"""Adds multiple ORM models to the session for insertion."""
		self.session.add_all(instances=orm_models)
		return orm_models

	async def flush(self) -> None:
		"""Flush pending changes without committing the transaction."""
		await self.session.flush()

	async def refresh(self, orm_model: OrmModelT) -> OrmModelT:
		"""Refreshes an ORM model from the database."""
		await self.session.refresh(instance=orm_model)
		return orm_model

	async def delete(self, orm_model: OrmModelT) -> None:
		"""Deletes an ORM model from the database."""
		await self.session.delete(instance=orm_model)
		return None
