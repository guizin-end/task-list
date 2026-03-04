import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

url = os.environ.get('DATABASE_URL')
engine = create_async_engine(url)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with async_session_factory() as session:
        yield session
