from pydantic import BaseModel
from typing import List, Tuple
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class Partida2(BaseModel):
    id: str | None = None
    jugador1: str | None = None
    jugador2: str | None = None
    turno: int | None = 0
    ronda: int | None = 0
    puntosJ1: int | None = 0
    puntosJ2: int | None = 0
    cantadoIdas: List[bool] | None = [False, False, False, False]
    cantadoVueltas: List[bool]  | None = [False, False, False, False]
    vueltas: bool | None = False
    arrastre: bool | None = False
    cartas: List[Tuple[str, int]] = []

class TokenData(BaseModel): 
    username: str | None = None

class RankingUser(BaseModel):
    username: str 
    lp: int | None = 0 #Puntos de Liga
    winMatches: int | None = 0
    looseMatches: int | None = 0

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
    perdedor: str 
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
