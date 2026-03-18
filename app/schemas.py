import enum
import uuid

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


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


class TodoSchema(BaseModel):
    title: str
    description: str


class TodoPublic(TodoSchema):
    id: uuid.UUID
    status: TodoStatus


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)


class TodoFilterQuery(FilterParams):
    title: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, max_length=20)
    status: TodoStatusPublic | None = None
