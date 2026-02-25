import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

url = os.environ.get('DATABASE_URL')
engine = create_async_engine(url)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
