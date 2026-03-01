from pydantic import BaseModel, EmailStr

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
