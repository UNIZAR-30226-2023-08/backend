from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Text
from database import Base

class Usuario(Base):
    __tablename__ = "Usuario"

    id = Column(String(30), primary_key=True, unique=True)
    nombre = Column(String(30))
    password = Column(String(30))
    correo = Column(String(50))