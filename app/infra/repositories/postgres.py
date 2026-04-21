"""app/infra/repositories/postgres.py"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.base import DeclarativeBaseModel
from app.infra.db.transaction import Transaction
from app.infra.repositories.interfaces.postgres import Repository


class PostgresRepository[OrmModelT: DeclarativeBaseModel](Repository[OrmModelT]):
	"""Generic repository for PostgreSQL database operations using SQLAlchemy."""

	orm_model: type[OrmModelT]

	def __init__(self, session: AsyncSession) -> None:
		"""Initializes the repository with a database session."""

		self.session: AsyncSession = session

	def transaction(self) -> Transaction[OrmModelT]:
		"""Creates a new transaction context."""

		return Transaction[OrmModelT](session=self.session)
