"""app/domain/schemas/user.py"""

from pydantic import EmailStr

from app.domain.models.enums.user import UserRoleEnum
from app.domain.schemas.base import OutSchema


class UserOutSchema(OutSchema):
	name: str
	email: EmailStr
	profile_image_url: str | None
	role: UserRoleEnum
	is_verified: bool
