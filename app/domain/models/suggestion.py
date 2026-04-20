"""app/domain/models/suggestion.py"""

from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel
from app.domain.models.enums.status import StatusEnum


class SuggestionModel(CreateBaseModel):
	__tablename__ = "suggestions"

	user_pk_id: Mapped[int] = mapped_column(ForeignKey("users.pk_id"))
	city_pk_id: Mapped[int] = mapped_column(ForeignKey("cities.pk_id"))
	category_pk_id: Mapped[int] = mapped_column(ForeignKey("categories.pk_id"))

	suggested_name: Mapped[str] = mapped_column(String(255))
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
	status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum))

	reviewed_by_pk_id: Mapped[int | None] = mapped_column(
		ForeignKey("users.pk_id"), nullable=True
	)
	reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)

	user: Mapped["UserModel"] = relationship(foreign_keys=[user_pk_id])  # noqa  # pyright: ignore
	city: Mapped["CityModel"] = relationship()  # noqa  # pyright: ignore
	category: Mapped["CategoryModel"] = relationship()  # noqa  # pyright: ignore
	reviewed_by: Mapped["UserModel | None"] = relationship(  # noqa  # pyright: ignore
		foreign_keys=[reviewed_by_pk_id]
	)
