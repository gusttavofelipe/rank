"""app/domain/schemas/auth.py"""

from pydantic import EmailStr, Field

from app.domain.schemas.base import BaseSchema


class UserRegisterSchema(BaseSchema):
	name: str = Field(min_length=2, max_length=255)
	email: EmailStr
	password: str = Field(min_length=8, max_length=128)
	profile_image_url: str | None = Field(default=None, max_length=500)


class UserLoginSchema(BaseSchema):
	email: EmailStr
	password: str = Field(min_length=8, max_length=128)


class TokenOutSchema(BaseSchema):
	access_token: str
	token_type: str = "bearer"


class LoginOutSchema(BaseSchema):
	# user: UserOutSchema
	tokens: TokenOutSchema
