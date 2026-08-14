from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Emprgit(Base):
    __tablename__ = 'empresa'