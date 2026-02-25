from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.security import authenticate_user, create_access_token, get_current_user

Session = Annotated[AsyncSession, Depends(get_session)]
AuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]
router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token')
async def login_for_access_token(form_data: AuthForm, session: Session):
    user = await authenticate_user(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password.',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {
        'access_token': create_access_token(data={'sub': user.email}),
        'token_type': 'bearer',
    }
