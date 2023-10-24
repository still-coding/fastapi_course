from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr

# TODO: make update optional

class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(UserBase):
    pass


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostWithVotes(PostResponse):
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class VoteDirection(Enum):
    UP = 1
    DOWN = 0


class Vote(BaseModel):
    post_id: int
    direction: VoteDirection
