from datetime import date
from pydantic import BaseModel

class Usuario(BaseModel):
    
    id: str
    nombre: str
    password: str
    correo: str
    
    class Config:
        orm_mode = True #will instruct Pydantic model to read the data as a dictionary and as an atribute
