from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models import User
from schemas import LoginModel, SignUpModel
from fastapi_jwt_auth import AuthJWT


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.username == email).first()


def jwt_required(Authorize: AuthJWT):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token wasn't provided"
        )


def super_user_required(Authorize: AuthJWT, db: Session):
    current_user = Authorize.get_jwt_subject()
    user = get_user_by_username(db, current_user)
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You aren't a superuser"
        )
