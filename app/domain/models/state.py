"""app/domain/models/state.py"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class StateModel(CreateBaseModel):
	__tablename__ = "states"

	country_pk_id: Mapped[int] = mapped_column(ForeignKey("countries.pk_id"))
	name: Mapped[str] = mapped_column(String(255))

	country: Mapped["CountryModel"] = relationship(back_populates="states")  # noqa  # pyright: ignore
	cities: Mapped[list["CityModel"]] = relationship(back_populates="state")  # noqa  # pyright: ignore
