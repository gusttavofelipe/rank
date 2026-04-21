"""app/api/v1/routers/user.py"""

from fastapi import APIRouter, status

from app.api.v1.dependencies.auth import CurrentUser
from app.domain.schemas.user import UserOutSchema, UserUpdateSchema
from app.domain.usecases.user import UserUsecaseDependency

router: APIRouter = APIRouter(prefix="/users", tags=["users"])


@router.patch(
	"/me",
	response_model=UserOutSchema,
	status_code=status.HTTP_200_OK,
	summary="Update user",
)
async def partial_update(
	usecase: UserUsecaseDependency,
	data: UserUpdateSchema,
	current_user: CurrentUser,
) -> UserOutSchema:
	result: UserOutSchema = await usecase.partial_update(data=data, id=current_user.id)
	return result
