import asyncio
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user
from app.models import User
from app.security import authenticate_user, create_access_token
from app.settings import get_settings

Session = Annotated[AsyncSession, Depends(get_session)]
AuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]
router = APIRouter(prefix='/auth', tags=['auth'])


r = Redis(host='redis', port=6379, decode_responses=True)
settings = get_settings()


@router.post('/token')
async def login_for_access_token(
    request: Request, form_data: AuthForm, session: Session
):
    username_key = f'login:{form_data.username}'
    ip = (
        request.headers
        .get('x-forwarded-for', request.client.host)
        .split(',')[0]
        .strip()
    )
    ip_key = f'login:{ip}'

    username_attempts, ip_attempts = await asyncio.gather(
        r.incr(username_key), r.incr(ip_key)
    )

    if max(username_attempts, ip_attempts) >= settings.LOGIN_ATTEMPTS_LIMIT:
        await asyncio.gather(
            r.expire(username_key, settings.LOGIN_LOCKOUT_TIME),
            r.expire(ip_key, settings.LOGIN_LOCKOUT_TIME),
        )
        raise HTTPException(
            status_code=HTTPStatus.TOO_MANY_REQUESTS, detail='Too many attempts.'
        )

    user = await authenticate_user(form_data.username, form_data.password, session)

    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password.',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    await asyncio.gather(r.delete(username_key), r.delete(ip_key))

    return {
        'access_token': create_access_token(data={'sub': user.email}),
        'token_type': 'bearer',
    }


@router.get('/token')
async def refresh_access_token(current_user: CurrentUser):
    return {
        'access_token': create_access_token(data={'sub': current_user.email}),
        'token_type': 'bearer',
    }
