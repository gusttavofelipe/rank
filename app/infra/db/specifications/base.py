"""app/infra/db/specifications/base.py"""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import ColumnElement, Select, not_, or_
from sqlalchemy.future import select as sa_select

from app.domain.models.base import DeclarativeBaseModel


class Specification[ModelT: DeclarativeBaseModel](ABC):
	@abstractmethod
	def apply(self, query: Select[tuple[ModelT]]) -> Select[tuple[ModelT]]: ...

	def __and__(self, other: "Specification[ModelT]") -> "AndSpecification[ModelT]":
		return AndSpecification(self, other)

	def __or__(self, other: "Specification[ModelT]") -> "OrSpecification[ModelT]":
		return OrSpecification(self, other)

	def __invert__(self) -> "NotSpecification[ModelT]":
		return NotSpecification(self)


class AndSpecification[ModelT: DeclarativeBaseModel](Specification[ModelT]):
	def __init__(
		self,
		left: Specification[ModelT],
		right: Specification[ModelT],
	) -> None:
		self.left = left
		self.right = right

	def apply(self, query: Select[tuple[ModelT]]) -> Select[tuple[ModelT]]:
		return self.right.apply(self.left.apply(query))


class OrSpecification[ModelT: DeclarativeBaseModel](Specification[ModelT]):
	def __init__(
		self,
		left: Specification[ModelT],
		right: Specification[ModelT],
	) -> None:
		self.left = left
		self.right = right

	def apply(self, query: Select[tuple[ModelT]]) -> Select[tuple[ModelT]]:
		base: type[ModelT] = query.column_descriptions[0]["entity"]
		left_query: Select[tuple[ModelT]] = self.left.apply(sa_select(base))
		right_query: Select[tuple[ModelT]] = self.right.apply(sa_select(base))

		left_clause: ColumnElement[Any] | None = left_query.whereclause
		right_clause: ColumnElement[Any] | None = right_query.whereclause

		if left_clause is None:
			return right_query
		if right_clause is None:
			return left_query

		return query.where(or_(left_clause, right_clause))


class NotSpecification[ModelT: DeclarativeBaseModel](Specification[ModelT]):
	def __init__(self, spec: Specification[ModelT]) -> None:
		self.spec = spec

	def apply(self, query: Select[tuple[ModelT]]) -> Select[tuple[ModelT]]:
		base: type[ModelT] = query.column_descriptions[0]["entity"]
		inner_query: Select[tuple[ModelT]] = self.spec.apply(sa_select(base))
		clause: ColumnElement[Any] | None = inner_query.whereclause

		if clause is None:
			return query

		return query.where(not_(clause))
