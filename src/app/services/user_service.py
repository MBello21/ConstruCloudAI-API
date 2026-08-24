from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..models.user import Users
from ..schemas.user import UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, password_hash)


def get_users(db: Session) -> List[Users]:
    """Lista todos los usuarios."""
    return db.query(Users).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[Users]:
    """Obtiene un usuario por ID. Retorna None si no existe."""
    return db.query(Users).filter(Users.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[Users]:
    """Obtiene un usuario por email. Retorna None si no existe."""
    return db.query(Users).filter(Users.email == email).first()


def create_user(db: Session, data: UserCreate) -> Users:
    """Crea un nuevo usuario. Lanza Exception si el email ya existe."""
    existing = get_user_by_email(db, data.email)
    if existing:
        raise Exception("User already exist.")

    new_user = Users(
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(
    db: Session,
    user_id: int,
    data: dict
) -> Optional[Users]:
    """Actualiza un usuario. Retorna None si no existe."""
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    for campo, valor in data.items():
        if campo == "password" and valor:
            setattr(user, "password_hash", hash_password(valor))
        else:
            setattr(user, campo, valor)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Elimina un usuario. Retorna True si se eliminó."""
    user = get_user_by_id(db, user_id)

    if not user:
        return False

    db.delete(user)
    db.commit()
    return True
