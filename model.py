from sqlalchemy.schema import Column
from sqlalchemy.types import String, Boolean
from sqlalchemy import text
from database import Base

class Usuario(Base):
    __tablename__ = "Usuario"

    username = Column(String(30), primary_key=True, unique=True)
    nombre = Column(String(30))
    hashed_password = Column(String(100), unique=True)
    correo = Column(String(50))
    disabled = Column(Boolean)
