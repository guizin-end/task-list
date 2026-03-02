from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_valid_todo
from app.models import Todo, TodoStatus, TodoStatusCreate, TodoStatusPublic, User
from app.schemas import FilterParamsTodos, TodoPublic, TodoSchema, TodoUpdate
from app.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_current_user)]
Db_Todo = Annotated[Todo, Depends(get_valid_todo)]
Filter_Query = Annotated[FilterParamsTodos, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    new_todo: TodoSchema,
    session: Session,
    current_user: Current_User,
    todo_status: TodoStatusCreate = TodoStatusPublic.DRAFT.value,
):
    db_todo = Todo(
        id=str(uuid4()),
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
    current_user: Current_User,
    filter_query: Filter_Query,
):
    params = [Todo.user_id == current_user.id]

    for key, value in filter_query.model_dump(
        exclude_none=True, exclude={'limit', 'offset'}
    ).items():
        params.append(getattr(Todo, key) == getattr(filter_query, key))

    return await session.scalars(
        select(Todo)
        .where(*params)
        .offset(filter_query.offset)
        .limit(filter_query.limit)
    )


@router.get('/trash', response_model=list[TodoPublic])
async def get_deleted_todos(
    session: Session,
    current_user: Current_User,
):
    return await session.scalars(
        select(Todo).where(
            Todo.user_id == current_user.id,
            Todo.status == TodoStatus.TRASH,
        )
    )


@router.delete('/trash', status_code=HTTPStatus.NO_CONTENT)
async def empty_trash(
    session: Session,
    current_user: Current_User,
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
    db_todo: Db_Todo,
    session: Session,
):
    db_todo.status = TodoStatus(status.value)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.patch('/{todo_id_or_title}', response_model=TodoPublic)  # noqa: FAST003
async def update_todo_data(
    new_todo_data: TodoUpdate,
    db_todo: Db_Todo,
    session: Session,
):
    for key, value in new_todo_data.model_dump(exclude_none=True).items():
        setattr(db_todo, key, value)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id_or_title}', status_code=HTTPStatus.NO_CONTENT)  # noqa: FAST003
async def delete_todo(
    db_todo: Db_Todo,
    session: Session,
):
    db_todo.status = TodoStatus.TRASH
    await session.commit()
