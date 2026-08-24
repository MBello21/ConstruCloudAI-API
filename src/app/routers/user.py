from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import UserCreate, UserResponse
from ..services.user_service import (
    get_users,
    get_user_by_id,
    create_user,
)

router = APIRouter()


@router.post('/', response_model=UserResponse, status_code=201)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = create_user(db, user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/', response_model=list[UserResponse])
def get_users_endpoint(db: Session = Depends(get_db)):
    return get_users(db)


@router.get('/{user_id}', response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user
