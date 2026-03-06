import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

url = os.environ.get('DATABASE_URL')
sync_engine = create_engine(url)
async_engine = create_async_engine(url)

sync_session_factory = sessionmaker(sync_engine, expire_on_commit=False)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session():
    async with async_session_factory() as session:
        yield session
