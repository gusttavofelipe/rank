"""app/api/v1/routers/country.py"""

import uuid

from fastapi import APIRouter, status

from app.api.v1.dependencies.auth import CurrentAdmin, CurrentUser
from app.domain.schemas.country import (
	CountryCreateSchema,
	CountryResponseSchema,
	CountryUpdateSchema,
)
from app.domain.usecases.country import CountryUsecaseDependency

router = APIRouter(prefix="/countries", tags=["countries"])


@router.post(
	"/",
	response_model=CountryResponseSchema,
	status_code=status.HTTP_201_CREATED,
	summary="Creates a new country (admin only)",
)
async def create(
	usecase: CountryUsecaseDependency,
	data: CountryCreateSchema,
	_: CurrentAdmin,
) -> CountryResponseSchema:
	return await usecase.create(data=data)


@router.patch(
	"/{id}",
	response_model=CountryResponseSchema,
	status_code=status.HTTP_201_CREATED,
	summary="Updates a country (admin only)",
)
async def partial_update(
	usecase: CountryUsecaseDependency,
	data: CountryUpdateSchema,
	id: uuid.UUID,
	_: CurrentAdmin,
) -> CountryResponseSchema:
	return await usecase.partial_update(data=data, id=id)


@router.get(
	"/{id}",
	response_model=CountryResponseSchema,
	status_code=status.HTTP_200_OK,
	summary="Get country by id",
)
async def get_by_id(
	id: uuid.UUID,
	usecase: CountryUsecaseDependency,
	_: CurrentUser,
) -> CountryResponseSchema:
	return await usecase.get_by_id(id=id)


@router.get(
	"/code/{code}",
	response_model=CountryResponseSchema,
	status_code=status.HTTP_200_OK,
	summary="Get country by code",
)
async def get_by_code(
	code: str,
	usecase: CountryUsecaseDependency,
	_: CurrentUser,
) -> CountryResponseSchema:
	return await usecase.get_by_code(code=code)


@router.get(
	"/",
	response_model=list[CountryResponseSchema],
	status_code=status.HTTP_200_OK,
	summary="List countries",
)
async def list_countries(
	usecase: CountryUsecaseDependency,
	_: CurrentUser,
	name: str = "",
) -> list[CountryResponseSchema]:
	return await usecase.list(name=name)
