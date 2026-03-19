import uuid
from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Todo, TodoStatus, User
from app.security import Token
from app.settings import get_settings

Session = Annotated[AsyncSession, Depends(get_session)]
settings = get_settings()


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


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_valid_todo(
    session: Session,
    current_user: CurrentUser,
    todo_id_or_title: str,
):
    try:
        todo_id = uuid.UUID(todo_id_or_title)
    except ValueError:
        todo_id = None

    db_todo = await session.scalar(
        select(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status != TodoStatus.TRASH,
            or_(
                Todo.title == todo_id_or_title, Todo.id == todo_id if todo_id else False
            ),
        )
    )

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Todo not found.')

    return db_todo
