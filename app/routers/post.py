from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])

# TODO: uptate queries to sqlalchemy 2.0 quering API

@router.get("/", response_model=List[schemas.PostWithVotes])
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = None,
):
    query = (
        select(
            models.Post.id,
            models.Post.title,
            models.Post.content,
            models.Post.published,
            models.Post.author_id,
            models.Post.created_at,
            func.count(models.Vote.user_id).label("votes"),
        )
        .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
        .group_by(models.Post.id)
    )
    if search:
        query = query.filter(models.Post.title.contains(search))
    ic(str(query))
    posts = db.execute(query.limit(limit).offset(skip))
    return posts


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> schemas.PostResponse:
    new_post = models.Post(author_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    ic(new_post)
    return new_post


@router.get("/latest", response_model=schemas.PostResponse)
def get_latest_post(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> schemas.PostResponse:
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no posts yet"
        )
    return post


@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> schemas.PostResponse:
    post = db.query(models.Post).filter(models.Post.id == id).first()
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> None:
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.get(models.Post, id)
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    db.delete(post)
    db.commit()


@router.put("/{id}")
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> schemas.PostResponse:
    post_to_update = db.get(models.Post, id)
    ic(post_to_update)
    if not post_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    if post_to_update.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    # TODO: check if there is a cleaner/faster way to update ORM object
    post_data = post.model_dump(exclude_unset=True)
    for k, v in post_data.items():
        setattr(post_to_update, k, v)
    db.add(post_to_update)
    db.commit()
    db.refresh(post_to_update)
    return post_to_update
