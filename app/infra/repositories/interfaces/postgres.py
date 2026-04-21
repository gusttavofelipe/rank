"""app/infra/repositories/interfaces/postgres.py"""

from abc import ABC, abstractmethod

from app.domain.models.base import DeclarativeBaseModel
from app.infra.db.specifications.base import Specification
from app.infra.db.transaction import Transaction


class Repository[OrmModelT: DeclarativeBaseModel](ABC):
	@abstractmethod
	async def create(
		self, orm_model: OrmModelT, transaction: Transaction[OrmModelT]
	) -> OrmModelT: ...

	@abstractmethod
	async def get(
		self,
		spec: Specification[OrmModelT],
		transaction: Transaction[OrmModelT] | None = None,
	) -> OrmModelT | None: ...
