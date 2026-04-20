"""app/infra/repositories/interfaces/postgres.py"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from app.domain.models.base import DeclarativeBaseModel
from app.infra.db.transaction import Transaction


class Repository[OrmModelT: DeclarativeBaseModel, FiltersT: Mapping[str, Any]](ABC):
	@abstractmethod
	async def create(
		self, orm_model: OrmModelT, transaction: Transaction[OrmModelT]
	) -> OrmModelT: ...

	@abstractmethod
	async def get(
		self, filters: FiltersT, transaction: Transaction[OrmModelT] | None = None
	) -> OrmModelT | None: ...

	# @abstractmethod
	# async def delete(
	# 	self, orm_model: OrmModelT, transaction: Transaction[OrmModelT]
	# ) -> None: ...
