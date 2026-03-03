from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Todo, TodoStatus, User
from app.security import get_current_user

Session = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_current_user)]


async def get_valid_todo(
    session: Session,
    current_user: Current_User,
    todo_id_or_title: str,
):
    db_todo = await session.scalar(
        select(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status != TodoStatus.TRASH,
            or_(Todo.title == todo_id_or_title, Todo.id == todo_id_or_title),
        )
    )

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Todo not found.')

    return db_todo
