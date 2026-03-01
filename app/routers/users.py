from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas import UserPublic, UserSchema, UserUpdate
from app.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(new_user: UserSchema, session: Session):
    db_user = User(
        id=str(uuid4()),
        username=new_user.username,
        email=new_user.email,
        password=get_password_hash(new_user.password),
    )

    try:
        session.add(db_user)
        await session.commit()

        return db_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists.'
        )


@router.get('/', response_model=list[UserPublic])
async def get_users(session: Session):
    return await session.scalars(select(User))


@router.get('/me', response_model=UserPublic)
async def get_me(current_user: Current_User):
    return current_user


@router.get('/{user_id}', response_model=UserPublic)
async def get_user_by_id(user_id: str, session: Session):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User does not exist.'
        )

    return db_user


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: str, new_user: UserSchema, session: Session, current_user: Current_User
):
    db_user = await session.scalar(
        select(User).where(
            User.id == user_id,
            User.id == current_user.id,
        )
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User does not exist.'
        )

    try:
        for key, value in new_user.model_dump().items():
            if key == 'password':
                setattr(db_user, key, get_password_hash(value))

            else:
                setattr(db_user, key, value)

        await session.commit()
        await session.refresh(db_user)

        return db_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists.'
        )


@router.patch('/{user_id}', response_model=UserPublic)
async def partial_update_user(
    user_id: str, user: UserUpdate, session: Session, current_user: Current_User
):
    db_user = await session.scalar(
        select(User).where(
            User.id == user_id,
            User.id == current_user.id,
        )
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User does not exist.'
        )

    try:
        for key, value in user.model_dump(exclude_unset=True).items():
            if key == 'password':
                setattr(db_user, key, get_password_hash(value))

            else:
                setattr(db_user, key, value)

        await session.commit()
        await session.refresh(db_user)

        return db_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists.'
        )


@router.delete('/{user_id}')
async def delete_user(user_id: str, session: Session, current_user: Current_User):
    db_user = await session.scalar(
        select(User).where(
            User.id == user_id,
            User.id == current_user.id,
        )
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User does not exist.'
        )

    await session.delete(db_user)
    await session.commit()

    return {'detail': 'User deleted.'}
