from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str 
    email: str | None = None
    real_name: str | None = None
    disabled: bool | None = False
    lp: int | None = 0 #Puntos de Liga
    coins: int | None = 0
    winMatches: int | None = 0
    looseMatches: int | None = 0
    winStreak: int | None = 0

class UserInDB(User):
    hashed_password: str

class PartidaDos(BaseModel):
    jugador1: str
    jugador2: str 
    ganador: str 
    puntosJ1: int 
    puntosJ2: int 
    fecha: str 

class PartidaTres(BaseModel):
    jugador1: str
    jugador2: str 
    jugador3: str
    ganador: str 
    puntosJ1: int 
    puntosJ2: int 
    puntosJ3: int 
    fecha: str 

class PartidaCuatro(BaseModel):
    jugador1: str 
    jugador2: str 
    jugador3: str 
    jugador4: str 
    puntosEquipo1: str 
    puntosEquipo2: str 
    ganadorJ1: str 
    ganadorJ2: str 
    fecha: str 
