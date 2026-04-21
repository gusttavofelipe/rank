"""app/domain/models/reviewed_entity.py"""

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel
from app.domain.models.enums.status import StatusEnum


class ReviewedEntityModel(CreateBaseModel):
	__tablename__: str = "reviewed_entities"

	city_pk_id: Mapped[int] = mapped_column(ForeignKey("cities.pk_id"))
	category_pk_id: Mapped[int] = mapped_column(ForeignKey("categories.pk_id"))

	name: Mapped[str] = mapped_column(String(255))
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
	role_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
	status: Mapped[StatusEnum]

	approved_by_pk_id: Mapped[int | None] = mapped_column(
		ForeignKey("users.pk_id"), nullable=True
	)
	approved_at: Mapped[datetime | None] = mapped_column(nullable=True)

	city: Mapped["CityModel"] = relationship(back_populates="reviewed_entities")  # noqa  # pyright: ignore
	category: Mapped["CategoryModel"] = relationship(back_populates="reviewed_entities")  # noqa  # pyright: ignore
	reviews: Mapped[list["ReviewModel"]] = relationship(back_populates="reviewed_entity")  # noqa  # pyright: ignore
	user_connections: Mapped[list["UserReviewedEntityModel"]] = relationship(  # noqa  # pyright: ignore
		back_populates="reviewed_entity"
	)
	approved_by: Mapped["UserModel | None"] = relationship(  # noqa  # pyright: ignore
		foreign_keys=[approved_by_pk_id]
	)
