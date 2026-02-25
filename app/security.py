from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.settings import get_settings

hasher = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl='auth/token', refreshUrl='auth/refresh_token')

Token = Annotated[str, Depends(oauth2)]
Session = Annotated[AsyncSession, Depends(get_session)]
settings = get_settings()
DUMMY_HASH = hasher.hash('dummypassword')


def get_password_hash(password: str):
    return hasher.hash(password)


def verify_password(plain_password, hashed_password):
    return hasher.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str, session: Session):
    db_user = await session.scalar(
        select(User).where(or_(User.email == username, User.username == username))
    )

    if not db_user:
        verify_password(password, DUMMY_HASH)
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Invalid username or password.',
        )

    if not verify_password(password, db_user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid username or password.'
        )

    return db_user


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    return encoded_jwt


async def get_current_user(token: Token, session: Session):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)

        username = payload.get('sub')
        if not username:
            raise credentials_exception

    except jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError:
        raise credentials_exception

    user = await session.scalar(select(User).where(User.email == username))

    if not user:
        raise credentials_exception

    return user
