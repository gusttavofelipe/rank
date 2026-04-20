"""app/infra/db/helpers/query_builder.py"""

from typing import Any

from sqlalchemy.future import select
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.selectable import Select

from app.domain.models.base import DeclarativeBaseModel


def apply_operator[OrmModelT: DeclarativeBaseModel](
	orm_model: type[OrmModelT], field: str, value: Any
) -> BinaryExpression[Any]:
	"""Return a SQLAlchemy condition for the given field
	and value with operator support.
	"""

	if "__" in field:
		col_name, op = field.split("__", 1)
	else:
		col_name, op = field, "eq"

	column = getattr(orm_model, col_name)

	if op == "eq":
		return column == value
	elif op == "ne":
		return column != value
	elif op == "lt":
		return column < value
	elif op == "lte":
		return column <= value
	elif op == "gt":
		return column > value
	elif op == "gte":
		return column >= value
	elif op == "in":
		return column.in_(value)
	else:
		raise ValueError(f"Unsupported operator: {op}")


def build_query[OrmModelT: DeclarativeBaseModel](
	orm_model: type[OrmModelT],
	filter: dict[str, Any] | None = None,
	return_conditions: bool = False,
) -> Select[tuple[OrmModelT]] | list[BinaryExpression[Any]]:
	"""Build a SQLAlchemy SELECT query for a given model with optional filters."""

	filters = filter or {}
	conditions: list[BinaryExpression[Any]] = [
		apply_operator(orm_model, key, value) for key, value in filters.items()
	]
	if return_conditions:
		return conditions

	query: Select[tuple[OrmModelT]] = select(orm_model)
	if conditions:
		query = query.where(*conditions)

	return query
