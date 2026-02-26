import os

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///:memory:')

from app.database import get_session
from app.main import app
from app.models import table_registry
from app.schemas import UserPublic
from app.security import get_current_user

users_payload = [
    {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    },
    {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'secret',
    },
]


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.connect() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.connect() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    def override_get_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = override_get_session
        yield client

    app.dependency_overrides.clear()


def create_user(payload, client):
    response = client.post(
        '/users',
        json=payload,
    )

    return response.json()


@pytest_asyncio.fixture
async def user(client):
    return create_user(users_payload[0], client)


@pytest_asyncio.fixture
async def other_user(client):
    return create_user(users_payload[1], client)


@pytest_asyncio.fixture
async def access_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': users_payload[0]['username'],
            'password': users_payload[0]['password'],
        },
    )

    return response.json()['access_token']


@pytest.fixture
def auth_headers(access_token: str):
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def mock_get_current_user(client, user):
    def override_get_current_user():
        return UserPublic.model_validate(user)

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def mock_authenticate_user(monkeypatch):
    async def fake_authenticate_user(username: str, password: str, session):
        return None

    monkeypatch.setattr('app.routers.auth.authenticate_user', fake_authenticate_user)


@pytest.fixture
def mock_decode_payload_no_username(monkeypatch):
    def fake_decode_payload(token, secret_key, algorithm):
        return {'mock': 'dict'}

    monkeypatch.setattr('app.security.jwt.decode', fake_decode_payload)


@pytest.fixture
def mock_decode_payload_with_mock_username(monkeypatch):
    def fake_decode_payload(token, secret_key, algorithm):
        return {'sub': 'mock_email@mock.com'}

    monkeypatch.setattr('app.security.jwt.decode', fake_decode_payload)
