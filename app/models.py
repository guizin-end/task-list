from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from app.schemas import TodoStatus

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False, repr=False)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, insert_default=uuid.uuid4, default_factory=uuid.uuid4
    )
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


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[TodoStatus] = mapped_column(
        default=TodoStatus.DRAFT,
        server_default=TodoStatus.DRAFT,
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, insert_default=uuid.uuid4, default_factory=uuid.uuid4
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
