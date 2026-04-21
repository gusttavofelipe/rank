"""app/domain/schemas/user.py"""

from pydantic import EmailStr, Field, HttpUrl

from app.domain.models.enums.user import UserRoleEnum
from app.domain.schemas.base import BaseSchema, OutSchema


class UserBaseSchema(OutSchema):
	name: str
	email: EmailStr
	profile_image_url: HttpUrl | None


class UserOutSchema(UserBaseSchema):
	role: UserRoleEnum
	is_verified: bool


class UserUpdateSchema(BaseSchema):
	name: str | None = Field(default=None, min_length=2, max_length=255)
	email: EmailStr | None = None
	profile_image_url: HttpUrl | None = Field(default=None, max_length=500)
