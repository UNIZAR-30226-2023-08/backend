from pydantic import BaseModel
from typing import List, Optional, Tuple
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class Partida2(BaseModel):
    id: Optional[str] = None
    estado: Optional[str] = "UNO"
    jugador1: Optional[str] = None
    jugador2: Optional[str] = None
    turno: Optional[int] = 0
    ronda: Optional[int] = 0
    puntosJ1: Optional[int] = 0
    puntosJ2: Optional[int] = 0
    manoJ1: List[tuple[str,int]] = []
    manoJ2: List[tuple[str,int]] = []
    cantadoIdas: Optional[List[bool]] = [False, False, False, False]
    cantadoVueltas: Optional[List[bool]] = [False, False, False, False]
    vueltas: Optional[bool] = False
    arrastre: Optional[bool] = False
    cartas: List[Tuple[str, int]] = []
    triunfo: Tuple[str, int] = [None, False]
    cartas_jugadas: Optional[List[Tuple[str,int]]] = [None, None]

class TokenData(BaseModel): 
    username: Optional[str] = None

class RankingUser(BaseModel):
    username: str 
    lp: Optional[int] = 0 #Puntos de Liga
    wonMatches: Optional[int] = 0
    lostMatches: Optional[int] = 0
    winStreak: Optional[int] = 0

class User(BaseModel):
    username: str 
    email: Optional[str] = None
    real_name: Optional[str] = None
    disabled: Optional[bool] = False
    lp: Optional[int] = 0 #Puntos de Liga
    coins: Optional[int] = 0
    wonMatches: Optional[int] = 0
    lostMatches: Optional[int] = 0
    winStreak: Optional[int] = 0

class Tienda(BaseModel):
    username: str 
    barajas: List[Tuple[str, int]] = []
    
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
