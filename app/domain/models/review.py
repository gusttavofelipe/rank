"""app/domain/models/review.py"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class ReviewModel(CreateBaseModel):
	__tablename__ = "reviews"

	reviewed_entity_pk_id: Mapped[int] = mapped_column(
		ForeignKey("reviewed_entities.pk_id")
	)
	user_pk_id: Mapped[int] = mapped_column(ForeignKey("users.pk_id"))

	rating: Mapped[int] = mapped_column(Integer)
	comment: Mapped[str | None] = mapped_column(Text, nullable=True)

	user: Mapped["UserModel"] = relationship(back_populates="reviews")  # noqa  # pyright: ignore
	reviewed_entity: Mapped["ReviewedEntityModel"] = relationship(  # noqa  # pyright: ignore
		back_populates="reviews"
	)
	response: Mapped["ReviewResponseModel | None"] = relationship(  # noqa  # pyright: ignore
		back_populates="review", uselist=False
	)
