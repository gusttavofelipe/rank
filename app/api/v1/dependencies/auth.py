# app/api/v1/dependencies/auth.py
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.jwt import decode_access_token
from app.domain.models.enums.user import UserRoleEnum
from app.domain.models.user import UserModel
from app.infra.db.manager import DatabaseManager
from app.infra.db.specifications.user import UserById
from app.infra.repositories.user import UserRepository

bearer_scheme = HTTPBearer()


async def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
	session: AsyncSession = Depends(DatabaseManager.get_session),
) -> UserModel:
	payload = decode_access_token(credentials.credentials)
	repo = UserRepository(session=session)
	user = await repo.get(UserById(uuid.UUID(payload["sub"])))
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
	return user


async def require_verified(
	current_user: UserModel = Depends(get_current_user),
) -> UserModel:
	if not current_user.is_verified:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail="Account not verified"
		)
	return current_user


async def require_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
	if current_user.role != UserRoleEnum.ADMIN:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
	return current_user


async def require_reviewed(
	current_user: UserModel = Depends(get_current_user),
) -> UserModel:
	if current_user.role != UserRoleEnum.REVIEWED:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
	return current_user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
CurrentAdmin = Annotated[UserModel, Depends(require_admin)]
CurrentReviewed = Annotated[UserModel, Depends(require_reviewed)]
CurrentVerified = Annotated[UserModel, Depends(require_verified)]
