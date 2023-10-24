from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db
from ..utils import verify_password

router = APIRouter(tags=["Authentication"])


@router.get("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    exc = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid credentials",
    )
    if not user:
        raise exc
    if not verify_password(user_credentials.password, user.password):
        raise exc

    token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": token, "token_type": "bearer"}
