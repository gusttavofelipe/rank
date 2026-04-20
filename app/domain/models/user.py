"""app/domain/models/user.py"""

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel
from app.domain.models.enums.user import UserRoleEnum


class UserModel(CreateBaseModel):
	__tablename__ = "users"

	name: Mapped[str] = mapped_column(String(255))
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	password_hash: Mapped[str] = mapped_column(String(255))
	profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
	role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum))
	is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

	reviews: Mapped[list["ReviewModel"]] = relationship(back_populates="user")  # noqa  # pyright: ignore
	reviewed_entities: Mapped[list["UserReviewedEntityModel"]] = relationship(  # noqa  # pyright: ignore
		back_populates="user"
	)
	refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(  # noqa  # pyright: ignore
		back_populates="user"
	)
