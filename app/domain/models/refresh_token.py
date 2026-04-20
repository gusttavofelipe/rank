"""app/domain/models/refresh_token.py"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class RefreshTokenModel(CreateBaseModel):
	__tablename__ = "refresh_tokens"

	user_pk_id: Mapped[int] = mapped_column(ForeignKey("users.pk_id"))
	token: Mapped[str] = mapped_column(String(512), unique=True, index=True)
	expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	revoked: Mapped[bool] = mapped_column(Boolean, default=False)

	user: Mapped["UserModel"] = relationship(back_populates="refresh_tokens")  # noqa  # pyright: ignore
