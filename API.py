
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import random
import asyncio

from datetime import timedelta
from fastapi.responses import HTMLResponse
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from Database.database import dbLogin
from Partidas.partida2 import actualizarEstadisticas2Jugadores
from chat import ChatManager
from login import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_active_user, get_password_hash
from Database.schema import User, UserInDB, Token

app = FastAPI()
global connected_clients_2
connected_clients_2 = {}
connected_clients_3 = {}
connected_clients_4 = {}



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


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    await actualizarEstadisticas2Jugadores(current_user.username, current_user.username)
    return current_user

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

#/////////////////////////////////////////////////////////////////////////////////

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

@app.get("/")
async def get():
    with open("index.html") as f:
        return HTMLResponse(f.read()) 

@app.get("/a")
async def get():
    with open("chat2.html") as f:
        return HTMLResponse(f.read()) 







@app.websocket("/partida/{num_jugadores}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, num_jugadores: int, client_id: str):
    global connected_clients_2
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            print(f'Mensaje recibido del cliente {client_id}: {message}')
            if num_jugadores == 1:
               print("al 1")     
            elif num_jugadores == 2:
                connected_clients_2[client_id] = websocket
                if len(connected_clients_2) == 2:
                    dir = crearDireccionRandom()
                    asyncio.create_task(partida2(dir, app))
                    await send_to_all_clients(str(dir), connected_clients_2)
                    connected_clients_2 = {}
                else:
                    await websocket.send_text("ESPERA")
            elif num_jugadores == 3:
                connected_clients_3[client_id] = websocket
                if len(connected_clients_2) == 3:
                    dir = crearDireccionRandom()
                    asyncio.create_task(partida2(dir))
                    await send_to_all_clients(str(dir), connected_clients_2)
                    connected_clients_2 = {}
                else:
                    await websocket.send_text("ESPERA")
            elif num_jugadores == 4:
                connected_clients_4[client_id] = websocket
                if len(connected_clients_2) == 4:
                    dir = crearDireccionRandom()
                    asyncio.create_task(partida2(dir))
                    await send_to_all_clients(str(dir), connected_clients_2)
                    connected_clients_2 = {}
                else:
                    await websocket.send_text("ESPERA")
             
    except WebSocketDisconnect:
        print("error")




async def send_to_all_clients(message: str, connected_clients: dict):
    for websocket in connected_clients.values():
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            pass
        
        
def crearDireccionRandom():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for i in range(5))