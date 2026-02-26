from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session


@pytest.mark.asyncio
async def test_get_session():
    db_gen = get_session()

    assert isinstance(db_gen, AsyncGenerator)
    db = await anext(db_gen)
    assert isinstance(db, AsyncSession)
