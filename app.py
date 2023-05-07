from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
import asyncio
import uuid
from random import randrange

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from Database.schema import Token
from Database.login import authenticate_user
from Database.database import dbLogin
from Database.login import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user, get_password_hash
from Database.schema import User, UserInDB
from Database.crud import obtenerTopJugadoresRanking
from Database.schema import RankingUser
from modelo_guinote.partida2Jugadores import buscarPartida
from modelo_guinote.partida2Jugadores import PartidaManager
from modelo_guinote.chat import ChatManager

from modelo_guinote.partida2 import Partida2
from modelo_guinote.partida3 import Partida3
from modelo_guinote.partida4 import Partida4

app = FastAPI()

partidas2_privadas = {}
partidas2_publicas = {}
partidas3_privadas = {}
partidas3_publicas = {}
partidas4_privadas = {}
partidas4_publicas = {}


 ##///////////INICIO SESION///////////////////

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(dbLogin, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register_user(register_user: UserInDB):
    hashed_password = get_password_hash(register_user.hashed_password)
    user_dict = register_user.dict()
    user_dict.pop("hashed_password")
    user_dict["hashed_password"] = hashed_password
    count = await dbLogin.count_documents({"username": register_user.username})
    if count > 0:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está en uso"
        )
    dbLogin.insert_one(user_dict)

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    top_users = await obtenerTopJugadoresRanking(10)
    for user in top_users:
        print(user["username"], user["lp"])

    return current_user

#/////////////////////////////////////////////////////////////////////////////////

#Partida de 2 jugadores        
@app.websocket("/partida2/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    partida_disponible = None
    for partida in partidas2_publicas.values():
        if partida.jugadores < 2:
            partida_disponible = partida
            break

    if not partida_disponible:
        partida_id = str(uuid.uuid4())
        partida_disponible = Partida2()
        partidas2_publicas[partida_id] = partida_disponible

    jugador_id = f"socket{partida_disponible.jugadores}"
    await partida_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await partida_disponible.remove_player(jugador_id)
        if partida_disponible.jugadores == 0:
            partidas2_publicas.pop(partida_id)
            
#Partida de 3 jugadores         
@app.websocket("/partida3/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    partida_disponible = None
    for partida in partidas3_publicas.values():
        if partida.jugadores < 3:
            partida_disponible = partida
            break

    if not partida_disponible:
        partida_id = str(uuid.uuid4())
        partida_disponible = Partida3()
        partidas3_publicas[partida_id] = partida_disponible

    jugador_id = f"socket{partida_disponible.jugadores}"
    await partida_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await partida_disponible.remove_player(jugador_id)
        if partida_disponible.jugadores == 0:
            partidas3_publicas.pop(partida_id)
            
#Partida de 4 jugadores         
@app.websocket("/partida4/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    partida_disponible = None
    for partida in partidas4_publicas.values():
        if partida.jugadores < 4:
            partida_disponible = partida
            break

    if not partida_disponible:
        partida_id = str(uuid.uuid4())
        partida_disponible = Partida4()
        partidas4_publicas[partida_id] = partida_disponible

    jugador_id = f"socket{partida_disponible.jugadores}"
    await partida_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await partida_disponible.remove_player(jugador_id)
        if partida_disponible.jugadores == 0:
            partidas4_publicas.pop(partida_id)
            
            
@app.post("/crear/partida2")
async def crear_partida():
    # Generar un número aleatorio entre 10000 y 99999 que no esté en uso
    while True:
        partida_id = str(randrange(10000, 100000))
        if partida_id not in partidas2_privadas:
            break

    partida_disponible = Partida2()
    partidas2_privadas[partida_id] = partida_disponible
    return {"codigo": partida_id}


# Unirse a una partida de 2 jugadores con un código
@app.websocket("/partida2/join/{client_id}/{codigo}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, codigo: str, ):
    await websocket.accept()

    if codigo not in partidas2_privadas:
        await websocket.send_text("Partida no encontrada.")
        await websocket.close()
        return

    partida_disponible = partidas2_privadas[codigo]

    if partida_disponible.jugadores >= 2:
        await websocket.send_text("Partida Llena.")
        await websocket.close()
        return

    jugador_id = f"socket{partida_disponible.jugadores}"
    await partida_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await partida_disponible.remove_player(jugador_id)
        if partida_disponible.jugadores == 0:
            partidas2_privadas.pop(codigo)
            

@app.post("/crear/partida3")
async def crear_partida():
    # Generar un número aleatorio entre 10000 y 99999 que no esté en uso
    while True:
        partida_id = str(randrange(10000, 100000))
        if partida_id not in partidas3_privadas:
            break

    partida_disponible = Partida3()
    partidas3_privadas[partida_id] = partida_disponible
    return {"codigo": partida_id}


# Unirse a una partida de 2 jugadores con un código
@app.websocket("/partida3/join/{client_id}/{codigo}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, codigo: str, ):
    await websocket.accept()

    if codigo not in partidas3_privadas:
        await websocket.send_text("Partida no encontrada.")
        await websocket.close()
        return

    partida_disponible = partidas3_privadas[codigo]

    if partida_disponible.jugadores >= 3:
        await websocket.send_text("Partida Llena.")
        await websocket.close()
        return

    jugador_id = f"socket{partida_disponible.jugadores}"
    await partida_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await partida_disponible.remove_player(jugador_id)
        if partida_disponible.jugadores == 0:
            partidas3_privadas.pop(codigo)
            
@app.post("/crear/partida4")
async def crear_partida():
    # Generar un número aleatorio entre 10000 y 99999 que no esté en uso
    while True:
        partida_id = str(randrange(10000, 100000))
        if partida_id not in partidas4_privadas:
            break

    partida_disponible = Partida4()
    partidas4_privadas[partida_id] = partida_disponible
    return {"codigo": partida_id}


# Unirse a una partida de 2 jugadores con un código
@app.websocket("/partida4/join/{client_id}/{codigo}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, codigo: str, ):
    await websocket.accept()

    if codigo not in partidas4_privadas:
        await websocket.send_text("Partida no encontrada.")
        await websocket.close()
        return

    partida_disponible = partidas4_privadas[codigo]

    if partida_disponible.jugadores >= 4:
        await websocket.send_text("Partida Llena.")
        await websocket.close()
        return

    jugador_id = f"socket{partida_disponible.jugadores}"
    await partida_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await partida_disponible.remove_player(jugador_id)
        if partida_disponible.jugadores == 0:
            partidas4_privadas.pop(codigo)

##//////////////////////////CHAT/////////////////////////////////////////////////

manager = ChatManager()
@app.websocket("/ws/{chat_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, username: str):
    await manager.connect(websocket, chat_id, username)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.receive(websocket, chat_id, username, data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, chat_id, username)
        
 ##//////////////////////////CHAT/////////////////////////////////////////////////
 #        
@app.get("/ranking", response_model = List[RankingUser])
async def read_users_me(limite_lista: int, current_user: User = Depends(get_current_active_user)):
    top_users = await obtenerTopJugadoresRanking(limite_lista)
    return top_users


managerPartidas2 = PartidaManager()
@app.websocket("/partida2/{partida_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, partida_id: str, username: str):
    await managerPartidas2.connect(websocket, partida_id, username)
    try:
        partida = await managerPartidas2.obtenerPartida(partida_id)
        print(partida["id"])
       
        while True:
            data = await websocket.receive_text()
            await manager.receive(websocket, partida_id, username, data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, partida_id, username)


@app.get("/buscarPartida")
async def read_users_me(idJugador:str, current_user: User = Depends(get_current_active_user)):
    id = await buscarPartida(idJugador)
    return id



