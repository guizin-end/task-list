from __future__ import annotations

import enum
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False, repr=False)

    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    todos: Mapped[List[Todo]] = relationship(
        init=False,
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
    )


class TodoStatus(str, enum.Enum):
    DRAFT = 'DRAFT'
    ACTIVE = 'ACTIVE'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    TRASH = 'TRASH'


class TodoStatusPublic(str, enum.Enum):
    DRAFT = 'DRAFT'
    ACTIVE = 'ACTIVE'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'


class TodoStatusCreate(str, enum.Enum):
    DRAFT = 'DRAFT'
    ACTIVE = 'ACTIVE'
    PENDING = 'PENDING'


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'
    __table_args__ = (UniqueConstraint('user_id', 'title', name='uq_todos_user_title'),)

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))

    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    status: Mapped[TodoStatus] = mapped_column(
        default=TodoStatus.PENDING,
        server_default=TodoStatus.PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(
        init=False,
        back_populates='todos',
        lazy='selectin',
    )
