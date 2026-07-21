from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..database import get_db
from ..models.user import Users
from ..schemas.user import UserCreate, UserResponse

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post('/', response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Users).filter(Users.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exist.")
    new_user = Users(
        email=user.email,
        username=user.username,
        password_hash=pwd_context.hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/', response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


@router.get('/{user_id}', response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user
