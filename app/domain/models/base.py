"""app/domain/models/base.py"""

import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, Integer, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DeclarativeBaseModel(DeclarativeBase): ...


IntPK = Annotated[
	int,
	mapped_column(
		Integer,
		primary_key=True,
	),
]

UUIDPublic = Annotated[
	uuid.UUID,
	mapped_column(
		Uuid(as_uuid=True),
		default=uuid.uuid4,
		unique=True,
		index=True,
		nullable=False,
	),
]

TZDatetime = Annotated[
	datetime,
	mapped_column(DateTime(timezone=True)),
]


class CreateBaseModel(DeclarativeBaseModel):
	__abstract__ = True

	pk_id: Mapped[IntPK]
	id: Mapped[UUIDPublic]

	created_at: Mapped[TZDatetime] = mapped_column(
		default=func.now(),
		server_default=func.now(),
	)
	updated_at: Mapped[TZDatetime] = mapped_column(
		default=func.now(),
		server_default=func.now(),
		onupdate=func.now(),
	)
