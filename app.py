from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uuid
import json
from random import randrange

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from Database.schema import Token
from Database.login import authenticate_user
from Database.database import dbLogin
from Database.login import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user, get_password_hash
from Database.schema import User, UserInDB
from Database.crud import cambiar_jugador_turno, obtener_triufo_partida, obtenerJugador, obtenerTopJugadoresRanking
from Database.schema import RankingUser
from modelo_guinote.logica_juego import que_jugador_gana_baza, sumar_puntos
from modelo_guinote.partida2Jugadores import buscarPartida
from modelo_guinote.partida2Jugadores import PartidaManager
from modelo_guinote.chat import ChatManager

from modelo_guinote.partida2 import Partida2
from modelo_guinote.partida3 import Partida3
from modelo_guinote.partida4 import Partida4
from modelo_guinote.partida2torneo import Partida2Torneo
from modelo_guinote.partidaIA import PartidaIA


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    return current_user

@app.get("/user/{username}")
async def read_users_stadistics(username: str, current_user: User = Depends(get_current_active_user)):
    usuario = await obtenerJugador(username)
    return usuario

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
    if limite_lista < 0:
        raise HTTPException(
            status_code=400,
            detail="El numero no es correcto"
        )
    top_users = await obtenerTopJugadoresRanking(limite_lista)
    return top_users


managerPartidas2 = PartidaManager()
@app.websocket("/partida2/{partida_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, partida_id: str, username: str):
    await managerPartidas2.connect(websocket, partida_id, username)
    await managerPartidas2.unirse_partida(websocket, partida_id, username)
    try:
        ##CHAT##
        #/ws/{partida_id}/{username} 
        if(await managerPartidas2.obtenerEstadoPartida(partida_id) == "UNO"):
            while(await managerPartidas2.obtener_jugadores_partida(partida_id) < 4):
                print("UNO")
                await asyncio.sleep(1)
        
        if(await managerPartidas2.obtenerEstadoPartida(partida_id) == "DOS"):
            print("EMPIEZA")
            print("DOS")
            if await managerPartidas2.obtener_jugador_turno(partida_id) == username:
                await managerPartidas2.comenzar_partida(partida_id)
            else:
                await asyncio.sleep(2)

            mano = await managerPartidas2.obtener_mano_jugador(partida_id, username)
            triunfo = await obtener_triufo_partida(partida_id)
            mano_send = {"Cartas": mano, "Triunfo": triunfo}
            await managerPartidas2.enviar_mensaje(mano_send, websocket)

            if await managerPartidas2.obtener_jugador_turno(partida_id) == username:
                await managerPartidas2.cambiarEstadoPartida(partida_id, "TRES")
            else:
                await asyncio.sleep(2)
        
        if await managerPartidas2.obtenerEstadoPartida(partida_id) == "TRES":

            if await managerPartidas2.obtener_jugador_turno(partida_id) == username:
                cartas_jugadas = await managerPartidas2.obtener_cartas_jugadas(partida_id)
                mano_send = {"0": cartas_jugadas[0], "1": cartas_jugadas[1] ,"Turno": username, "Triunfo": triunfo}
                await managerPartidas2.enviar_mensaje(mano_send, websocket)
                carta = await managerPartidas2.esperar_mensaje(websocket)
                palo, valor = carta.split("-")
                carta_tupla = [str(palo), int(valor)]
                mano.remove(carta_tupla)
                await managerPartidas2.cambiar_mano_jugador(partida_id, username, mano)

                cartas_jugadas[0] = carta_tupla
                await managerPartidas2.cambiar_cartas_jugadas(partida_id, cartas_jugadas)
                await managerPartidas2.cambiar_jugador_turno(partida_id)

                while await managerPartidas2.obtener_jugador_turno(partida_id) != username:
                    await asyncio.sleep(1)
                
            else:
                while await managerPartidas2.obtener_jugador_turno(partida_id) != username:
                    await asyncio.sleep(1)
                cartas_jugadas = await managerPartidas2.obtener_cartas_jugadas(partida_id)
                mano_send = {"0": cartas_jugadas[0], "1": cartas_jugadas[1] ,"Turno": username, "Triunfo": triunfo}
                await managerPartidas2.enviar_mensaje(mano_send, websocket)
                carta = await managerPartidas2.esperar_mensaje(websocket)
                palo, valor = carta.split("-")
                carta_tupla = [str(palo), int(valor)]
                mano.remove(carta_tupla)
                await managerPartidas2.cambiar_mano_jugador(partida_id, username, mano)

                cartas_jugadas[1] = carta_tupla
                await managerPartidas2.cambiar_cartas_jugadas(partida_id, cartas_jugadas)
                await managerPartidas2.cambiar_jugador_turno(partida_id)
                ##Controlar resultado

            cartas_jugadas = await managerPartidas2.obtener_cartas_jugadas(partida_id)
            mano_send = {"0": cartas_jugadas[0], "1": cartas_jugadas[1] ,"Turno": None, "Triunfo": triunfo}
            await managerPartidas2.enviar_mensaje(mano_send, websocket)  

            if await managerPartidas2.obtener_jugador_turno(partida_id) == username:
                carta_gandora = que_jugador_gana_baza(cartas_jugadas, triunfo) 
                indice_ganador = cartas_jugadas.index(carta_gandora)
                #Sumo puntos al jugador que ha ganado la baza
                if await managerPartidas2.obtener_turno(partida_id) == indice_ganador:
                    puntosJugador0 = sumar_puntos(cartas_jugadas)
                    await managerPartidas2.cambiar_puntos_jugador(partida_id, puntosJugador0, indice_ganador)
                    message_ganador = {"Ganador": "0"}
                    await managerPartidas2.enviar_mensaje_todos(partida_id, message_ganador)
                    puede_cantar_cambiar = 0
                else:
                    puntosJugador1 = sumar_puntos(cartas_jugadas)
                    await managerPartidas2.cambiar_puntos_jugador(partida_id, puntosJugador1, indice_ganador)
                    message_ganador = {"Ganador": "1"}
                    await managerPartidas2.enviar_mensaje_todos(partida_id, message_ganador)
                    await cambiar_jugador_turno(partida_id)
                    puede_cantar_cambiar = 1
            else:
                await asyncio.sleep(2)
                




        partida = await managerPartidas2.obtenerPartida(partida_id)

        await managerPartidas2.cambiarEstadoPartida(partida_id, "UNO")

       
        while True:
            data = await websocket.receive_text()
            await manager.receive(websocket, partida_id, username, data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, partida_id, username)


@app.get("/buscarPartida")
async def read_users_me(idJugador:str, current_user: User = Depends(get_current_active_user)):
    id = await buscarPartida(idJugador)
    return id



partidas_torneo = {}

class Torneo:
    def __init__(self):
        self.partidas_inicial = []
        self.partidas_final = None
        self.ganadores = []
        self.lista_de_espera = []
        self.websocket_ganadores = {}

    async def send_message_to_socket(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def add_player(self, websocket: WebSocket, client_id: str):
        self.lista_de_espera.append((websocket, client_id))

        # Enviar mensaje a todos los jugadores con la lista de client_id actualizada
        message = json.dumps({str(i): (self.lista_de_espera[i][1] if i < len(self.lista_de_espera) else None) for i in range(4)})
        for ws, _ in self.lista_de_espera:
            await self.send_message_to_socket(ws, message)

        if len(self.lista_de_espera) >= 4:
            partidas_tasks = []
            jugadores_partidas_iniciales = []
            for _ in range(2):
                jugadores_partidas_iniciales.extend(self.lista_de_espera[:2])
                self.lista_de_espera = self.lista_de_espera[2:]

                partida = Partida2Torneo()
                self.partidas_inicial.append(partida)
                partidas_tasks.append(partida.add_player(jugadores_partidas_iniciales[-2][0], jugadores_partidas_iniciales[-2][1]))
                partidas_tasks.append(partida.add_player(jugadores_partidas_iniciales[-1][0], jugadores_partidas_iniciales[-1][1]))

            self.ganadores = await asyncio.gather(*partidas_tasks)

            for i in range(0, len(self.ganadores), 2):
                if self.ganadores[i] is not None:
                    self.websocket_ganadores[self.ganadores[i]] = jugadores_partidas_iniciales[i][0]
                if self.ganadores[i + 1] is not None:
                    self.websocket_ganadores[self.ganadores[i + 1]] = jugadores_partidas_iniciales[i + 1][0]

            self.ganadores = [ganador for ganador in self.ganadores if ganador is not None]
            
            
            # Enviar mensaje a todos los
            message = json.dumps({"Ganador Partida1": self.ganadores[0], "Ganador Partida2": self.ganadores[1]})
            for ws, _ in jugadores_partidas_iniciales:
                await self.send_message_to_socket(ws, message)

            if len(self.ganadores) == 2:
                partida_final = Partida2Torneo()
                self.partidas_final = partida_final
                ws_ganador1 = self.websocket_ganadores[self.ganadores[0]]
                ws_ganador2 = self.websocket_ganadores[self.ganadores[1]]
                ganador_final = await partida_final.add_player(ws_ganador1, self.ganadores[0])
                ganador_final = await partida_final.add_player(ws_ganador2, self.ganadores[1])

                # Enviar mensaje a todos los
                message = json.dumps({"Ganador Torneo: ": ganador_final})
                for ws, _ in jugadores_partidas_iniciales:
                    await self.send_message_to_socket(ws, message)


@app.websocket("/torneo/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    torneo_disponible = None
    for torneo in partidas_torneo.values():
        if len(torneo.partidas_inicial) < 2 or any(partida.jugadores < 2 for partida in torneo.partidas_inicial):
            torneo_disponible = torneo
            break

    if not torneo_disponible:
        torneo_id = str(uuid.uuid4())
        torneo_disponible = Torneo()
        partidas_torneo[torneo_id] = torneo_disponible
        
    await torneo_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    
partidas2_IA = {}
      
#Partida de 2 jugadores IA      
@app.websocket("/partidaIA/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()

    partida_id = str(uuid.uuid4())
    partida_disponible = PartidaIA()
    partidas2_IA[partida_id] = partida_disponible

    jugador_id = f"socket{partida_disponible.jugadores}"
    await partida_disponible.add_player(websocket, client_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await partida_disponible.remove_player(jugador_id)
        if partida_disponible.jugadores == 0:
            partidas2_IA.pop(partida_id)




