from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_valid_todo
from app.models import Todo, User
from app.schemas import (
    FilterParamsTodos,
    TodoPublic,
    TodoSchema,
    TodoStatus,
    TodoStatusCreate,
    TodoStatusPublic,
    TodoUpdate,
)
from app.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
DbTodo = Annotated[Todo, Depends(get_valid_todo)]
FilterQuery = Annotated[FilterParamsTodos, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    new_todo: TodoSchema,
    session: Session,
    current_user: CurrentUser,
    todo_status: TodoStatusCreate = TodoStatusPublic.DRAFT.value,
):
    db_todo = Todo(
        title=new_todo.title,
        description=new_todo.description,
        status=todo_status.value,
        user_id=current_user.id,
    )
    session.add(db_todo)
    await session.commit()

    return db_todo


@router.get('/', response_model=list[TodoPublic])
async def get_todos(
    session: Session,
    current_user: CurrentUser,
    filter_query: FilterQuery,
):
    params = [Todo.user_id == current_user.id]

    for key, value in filter_query.model_dump(
        exclude_none=True, exclude={'limit', 'offset'}
    ).items():
        if key == 'title':
            params.append(getattr(Todo, key).contains(value))
        else:
            params.append(getattr(Todo, key) == value)

    return await session.scalars(
        select(Todo)
        .where(*params)
        .offset(filter_query.offset)
        .limit(filter_query.limit)
    )


@router.get('/trash', response_model=list[TodoPublic])
async def get_deleted_todos(
    session: Session,
    current_user: CurrentUser,
):
    return await session.scalars(
        select(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.TRASH,
        )
    )


@router.delete('/trash', status_code=HTTPStatus.NO_CONTENT)
async def empty_user_todo_trash(
    session: Session,
    current_user: CurrentUser,
):
    await session.execute(
        delete(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.TRASH,
        )
    )
    await session.commit()


@router.patch('/{todo_id_or_title}/status', response_model=TodoPublic)  # noqa: FAST003
async def update_todo_status(
    status: TodoStatusPublic,
    db_todo: DbTodo,
    session: Session,
):
    db_todo.status = TodoStatus(status.value)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.patch('/{todo_id_or_title}', response_model=TodoPublic)  # noqa: FAST003
async def update_todo_data(
    new_todo_data: TodoUpdate,
    db_todo: DbTodo,
    session: Session,
):
    for key, value in new_todo_data.model_dump(exclude_none=True).items():
        setattr(db_todo, key, value)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id_or_title}', status_code=HTTPStatus.NO_CONTENT)  # noqa: FAST003
async def delete_todo(
    db_todo: DbTodo,
    session: Session,
):
    db_todo.status = TodoStatus.TRASH
    await session.commit()
