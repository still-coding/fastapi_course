from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, Identity, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str]
    published: Mapped[bool] = mapped_column(server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.CURRENT_TIMESTAMP()
    )

    author: Mapped["User"] = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"Post(id={self.id}, title={self.title}, created_at={self.created_at})"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.CURRENT_TIMESTAMP()
    )
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="author")

    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, created_at={self.created_at})"
