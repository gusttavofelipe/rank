"""app/domain/models/user_reviewed_entity.py"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class UserReviewedEntityModel(CreateBaseModel):
	__tablename__: str = "user_reviewed_entities"

	user_pk_id: Mapped[int] = mapped_column(ForeignKey("users.pk_id"))
	reviewed_entity_pk_id: Mapped[int] = mapped_column(
		ForeignKey("reviewed_entities.pk_id")
	)

	user: Mapped["UserModel"] = relationship(back_populates="reviewed_entities")  # noqa  # pyright: ignore
	reviewed_entity: Mapped["ReviewedEntityModel"] = relationship(  # noqa  # pyright: ignore
		back_populates="user_connections"
	)
	responses: Mapped[list["ReviewResponseModel"]] = relationship(  # noqa  # pyright: ignore
		back_populates="user_reviewed_entity"
	)
