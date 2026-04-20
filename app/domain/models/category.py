"""app/domain/models/category.py"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class CategoryModel(CreateBaseModel):
	__tablename__ = "categories"

	name: Mapped[str] = mapped_column(String(255))
	slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	icon: Mapped[str | None] = mapped_column(String(255), nullable=True)

	reviewed_entities: Mapped[list["ReviewedEntityModel"]] = relationship(  # noqa  # pyright: ignore
		back_populates="category"
	)
