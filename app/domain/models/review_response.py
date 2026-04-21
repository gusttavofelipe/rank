"""app/domain/models/review_response.py"""

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class ReviewResponseModel(CreateBaseModel):
	__tablename__: str = "review_responses"

	review_pk_id: Mapped[int] = mapped_column(ForeignKey("reviews.pk_id"))
	user_reviewed_entity_pk_id: Mapped[int] = mapped_column(
		ForeignKey("user_reviewed_entities.pk_id")
	)

	content: Mapped[str] = mapped_column(Text)

	review: Mapped["ReviewModel"] = relationship(back_populates="response")  # noqa  # pyright: ignore
	user_reviewed_entity: Mapped["UserReviewedEntityModel"] = relationship(  # noqa  # pyright: ignore
		back_populates="responses"
	)
