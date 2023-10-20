from sqlalchemy import Identity, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import String
from sqlalchemy.sql.expression import text

from datetime import datetime

class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str]
    published: Mapped[bool] = mapped_column(server_default='true')
    created_at: Mapped[datetime] = mapped_column(server_default=func.CURRENT_TIMESTAMP())

    def __repr__(self):
        return f'Post(id={self.id}, title={self.title}, created_at={self.created_at})'