from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix='/posts', tags=['Posts'])


@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)) -> List[schemas.PostResponse]:
    posts = db.query(models.Post).all()
    ic(posts)
    return posts


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    post: schemas.PostCreate, db: Session = Depends(get_db)
) -> schemas.PostResponse:
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    ic(new_post)
    return new_post


@router.get("/latest", response_model=schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db)) -> schemas.PostResponse:
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no posts yet"
        )
    return post


@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db)) -> schemas.PostResponse:
    post = db.query(models.Post).filter(models.Post.id == id).first()
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)) -> None:
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.get(models.Post, id)
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )
    db.delete(post)
    db.commit()


@router.put("/{id}")
def update_post(
    id: int, post: schemas.PostCreate, db: Session = Depends(get_db)
) -> schemas.PostResponse:
    post_to_update = db.get(models.Post, id)
    ic(post_to_update)
    if not post_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    # TODO: check if there is a cleaner/faster way to update ORM object
    post_data = post.model_dump(exclude_unset=True)
    for k, v in post_data.items():
        setattr(post_to_update, k, v)
    db.add(post_to_update)
    db.commit()
    db.refresh(post_to_update)
    return post_to_update
