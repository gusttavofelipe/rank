"""app/domain/schemas/base.py"""

from datetime import datetime
from typing import ClassVar

from pydantic import UUID4, BaseModel, ConfigDict


class BaseSchema(BaseModel):
	model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class OutSchema(BaseSchema):
	id: UUID4
	created_at: datetime
	updated_at: datetime
