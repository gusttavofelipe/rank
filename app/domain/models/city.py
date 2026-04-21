"""app/domain/models/city.py"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import CreateBaseModel


class CityModel(CreateBaseModel):
	__tablename__: str = "cities"

	state_pk_id: Mapped[int] = mapped_column(ForeignKey("states.pk_id"))
	name: Mapped[str] = mapped_column(String(255))

	state: Mapped["StateModel"] = relationship(back_populates="cities")  # noqa  # pyright: ignore
	reviewed_entities: Mapped[list["ReviewedEntityModel"]] = relationship(  # noqa  # pyright: ignore
		back_populates="city"
	)
