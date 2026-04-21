"""app/api/v1/routers/category.py"""

import uuid

from fastapi import APIRouter, status

from app.api.v1.dependencies.auth import CurrentAdmin, CurrentUser
from app.domain.schemas.category import (
	CategoryCreateSchema,
	CategoryResponseSchema,
	CategoryUpdateSchema,
)
from app.domain.usecases.category import CategoryUsecaseDependency

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
	"/",
	response_model=CategoryResponseSchema,
	status_code=status.HTTP_201_CREATED,
	summary="Creates a new category (admin only)",
)
async def create(
	usecase: CategoryUsecaseDependency,
	data: CategoryCreateSchema,
	_: CurrentAdmin,
) -> CategoryResponseSchema:
	return await usecase.create(data=data)


@router.patch(
	"/{id}",
	response_model=CategoryResponseSchema,
	status_code=status.HTTP_201_CREATED,
	summary="Updates a category (admin only)",
)
async def partial_update(
	usecase: CategoryUsecaseDependency,
	data: CategoryUpdateSchema,
	category_id: uuid.UUID,
	_: CurrentAdmin,
) -> CategoryResponseSchema:
	return await usecase.partial_update(data=data, id=category_id)


@router.get(
	"/{id}",
	response_model=CategoryResponseSchema,
	status_code=status.HTTP_200_OK,
	summary="Get category by id",
)
async def get_by_id(
	id: uuid.UUID,
	usecase: CategoryUsecaseDependency,
	_: CurrentUser,
) -> CategoryResponseSchema:
	return await usecase.get_by_id(id=id)


@router.get(
	"/slug/{slug}",
	response_model=CategoryResponseSchema,
	status_code=status.HTTP_200_OK,
	summary="Get category by slug",
)
async def get_by_slug(
	slug: str,
	usecase: CategoryUsecaseDependency,
	_: CurrentUser,
) -> CategoryResponseSchema:
	return await usecase.get_by_slug(slug=slug)


@router.get(
	"/",
	response_model=list[CategoryResponseSchema],
	status_code=status.HTTP_200_OK,
	summary="List categories",
)
async def list_categories(
	_: CurrentUser,
	usecase: CategoryUsecaseDependency,
	name: str = "",
) -> list[CategoryResponseSchema]:
	return await usecase.list(name=name)
