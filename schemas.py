
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class MemoryCreate(BaseModel):
    user_id: int
    content: str


class EventCreate(BaseModel):
    user_id: int
    title: str
    description: str = ""


print("schemas.py created successfully!")
