"""app/api/v1/routers/auth.py"""

from fastapi import APIRouter, Cookie, Response, status

from app.api.v1.dependencies.auth import CurrentUser
from app.core.config import settings
from app.domain.schemas.auth import (
	LoginOutSchema,
	TokenOutSchema,
	UserLoginSchema,
	UserRegisterSchema,
)
from app.domain.schemas.user import UserOutSchema
from app.domain.usecases.auth import AuthUsecaseDependency

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
	"/register",
	response_model=UserOutSchema,
	status_code=status.HTTP_201_CREATED,
	summary="Register a new user",
)
async def register(
	usecase: AuthUsecaseDependency,
	data: UserRegisterSchema,
) -> UserOutSchema:
	return await usecase.register(data=data)


@router.post(
	"/login",
	response_model=LoginOutSchema,
	status_code=status.HTTP_200_OK,
	summary="Login",
)
async def login(
	response: Response,
	usecase: AuthUsecaseDependency,
	data: UserLoginSchema,
) -> LoginOutSchema:
	result: LoginOutSchema
	refresh_token: str
	result, refresh_token = await usecase.login(data=data)
	response.set_cookie(
		key=settings.REFRESH_TOKEN_COOKIE,
		value=refresh_token,
		httponly=True,
		secure=True,
		samesite="strict",
		max_age=settings.REFRESH_TOKEN_MAX_AGE,
	)
	return result


@router.post(
	"/refresh",
	response_model=TokenOutSchema,
	status_code=status.HTTP_200_OK,
	summary="Refresh access token",
)
async def refresh(
	response: Response,
	usecase: AuthUsecaseDependency,
	refresh_token: str = Cookie(alias=settings.REFRESH_TOKEN_COOKIE),
) -> TokenOutSchema:
	tokens: TokenOutSchema
	new_refresh_token: str
	tokens, new_refresh_token = await usecase.refresh(refresh_token_str=refresh_token)
	response.set_cookie(
		key=settings.REFRESH_TOKEN_COOKIE,
		value=new_refresh_token,
		httponly=True,
		secure=True,
		samesite="strict",
		max_age=settings.REFRESH_TOKEN_MAX_AGE,
	)
	return tokens


@router.post(
	"/logout",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Logout",
)
async def logout(
	response: Response,
	usecase: AuthUsecaseDependency,
	refresh_token: str = Cookie(alias=settings.REFRESH_TOKEN_COOKIE),
) -> None:
	await usecase.logout(refresh_token_str=refresh_token)
	response.delete_cookie(settings.REFRESH_TOKEN_COOKIE)


@router.get(
	"/me",
	response_model=UserOutSchema,
	status_code=status.HTTP_200_OK,
	summary="Get current authenticated user",
)
async def me(
	usecase: AuthUsecaseDependency,
	current_user: CurrentUser,
) -> UserOutSchema:
	return await usecase.me(user=current_user)
