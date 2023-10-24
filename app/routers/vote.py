from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..oauth2 import get_current_user
from ..schemas import Vote, VoteDirection
from ..utils import hash_password

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: Vote,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
) -> dict:
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id: {vote.post_id} does not exist",
        )

    found_vote = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == user.id
    ).first()
    if vote.direction == VoteDirection.UP:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User id: {user.id} has already voted for post id: {vote.post_id}",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added vote"}
    
    if not found_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote does not exist",
        )
    db.delete(found_vote)
    db.commit()
    return {"message": "successfully deleted vote"}
