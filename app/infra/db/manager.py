"""app/infra/db/manager.py"""

from collections.abc import AsyncGenerator
from typing import Annotated

from asyncpg import Pool, create_pool
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)

from app.core.config import settings


class DatabaseManager:
	_engine: AsyncEngine | None = None
	_sessionmaker: async_sessionmaker[AsyncSession] | None = None
	_pool: Pool | None = None

	@classmethod
	def get_engine(cls) -> AsyncEngine:
		if cls._engine is None:
			cls._engine = create_async_engine(
				settings.DATABASE_URL,
				echo=False,
				pool_pre_ping=True,
				pool_size=20,
				max_overflow=40,
				pool_recycle=1800,
				future=True,
			)
		return cls._engine

	@classmethod
	def get_sessionmaker(cls) -> async_sessionmaker[AsyncSession]:
		if cls._sessionmaker is None:
			cls._sessionmaker = async_sessionmaker(
				bind=cls.get_engine(),
				expire_on_commit=False,
				class_=AsyncSession,
			)
		return cls._sessionmaker

	@classmethod
	async def get_session(cls) -> AsyncGenerator[AsyncSession]:
		"""Provides a database session with automatic cleanup."""
		async_session = cls.get_sessionmaker()
		async with async_session() as session:
			yield session

	@classmethod
	async def get_asyncpg_pool(cls) -> Pool:
		if cls._pool is None:
			dsn: str = settings.DATABASE_URL.replace("+asyncpg", "")
			cls._pool = await create_pool(dsn=dsn, min_size=5, max_size=20)
			# increase to min_size=10, max_size=50 if it's to insert millions
		return cls._pool

	@classmethod
	async def test_connection(cls) -> bool:
		"""Tests the database connection."""
		async_session = cls.get_sessionmaker()

		async with async_session() as session:
			await session.execute(text("SELECT 1"))
			return True


DatabaseDependency = Annotated[AsyncSession, Depends(DatabaseManager.get_session)]
