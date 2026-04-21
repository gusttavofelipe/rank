"""app/domain/models/country.py"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class CountryModel(CreateBaseModel):
	__tablename__: str = "countries"

	name: Mapped[str] = mapped_column(String(255))
	code: Mapped[str] = mapped_column(String(3), unique=True, index=True)

	states: Mapped[list["StateModel"]] = relationship(back_populates="country")  # noqa  # pyright: ignore
