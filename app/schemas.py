from pydantic import BaseModel, EmailStr, Field

from app.models import TodoStatus


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class TodoSchema(BaseModel):
    title: str
    description: str


class TodoPublic(TodoSchema):
    id: str
    status: TodoStatus


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
