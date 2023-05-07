from Database.schema import Partida2
from Database.database import dbPartida2Jugadores
import uuid
from typing import List
from fastapi import WebSocket
from pydantic import BaseModel

from Database.crud import insertarPartida2Jugadores
from Database.crud import buscarPartida2Jugadores
from Database.crud import buscarPartidaEmpezada
from Database.crud import obtenerPartida


async def crearPartida(jugador: str):
    idPartida = str(uuid.uuid4())  # Generar un UUID único para la partida
    # Guardar la partida en la base de datos dbPartida2Jugadores
    partidaNueva = Partida2(
        id= idPartida
    )
    partidaNueva_dict = partidaNueva.dict()
    partidaNueva_dict["jugador1"] = jugador
    await insertarPartida2Jugadores(partidaNueva_dict)
    return partidaNueva_dict["id"]

async def buscarPartida(jugador: str):
    id = await buscarPartidaEmpezada(jugador)
    if id:
        return id
    else:
        # Buscar partida con un jugador a null
        partida = await buscarPartida2Jugadores(jugador)
        if partida:
            # Se encontró una partida con un jugador a null, seleccionarla
            return partida["id"]
        else:
            # No se encontró una partida con un jugador a null, crear una nueva partida
            id = await crearPartida(jugador)
            return id
            
class PlayerMessage(BaseModel):
    username: str
    message: str

class Partida:
    def __init__(self, partida_id: str):
        self.partida_id = partida_id
        self.jugadores = []

    def agregar_jugador(self, username: str, websocket: WebSocket):
        self.jugadores.append((username, websocket))

    def eliminar_jugador(self, websocket: WebSocket):
        self.jugadores = [(username, ws) for username, ws in self.jugadores if ws != websocket]

    async def enviar_mensaje(self, message: str):
        for _, ws in self.jugadores:
            await ws.send_text(message)

class PartidaManager:
    def __init__(self):
        self.partidas = {}

    async def connect(self, websocket: WebSocket, partida_id: str, username: str):
        await websocket.accept()
        await self.unirse_partida(websocket, partida_id, username)
        await self.enviar_mensaje(partida_id, f"{username} se ha unido a la partida.")

    async def receive(self, websocket: WebSocket, partida_id: str, username: str, message: str):
        player_message = PlayerMessage(username=username, message=message)
        await self.enviar_mensaje(partida_id, player_message.json())

    async def disconnect(self, websocket: WebSocket, partida_id: str, username: str):
        await self.eliminar_jugador(websocket, partida_id, username)
        await self.enviar_mensaje(partida_id, f"{username} ha abandonado la partida.")

    async def unirse_partida(self, websocket: WebSocket, partida_id: str, username: str):
        if partida_id not in self.partidas:
            self.partidas[partida_id] = Partida(partida_id)
        partida = self.partidas[partida_id]
        partida.agregar_jugador(username, websocket)

    async def eliminar_jugador(self, websocket: WebSocket, partida_id: str, username: str):
        if partida_id in self.partidas:
            partida = self.partidas[partida_id]
            partida.eliminar_jugador(websocket)

    async def enviar_mensaje(self, partida_id: str, message: str):
        if partida_id in self.partidas:
            partida = self.partidas[partida_id]
            await partida.enviar_mensaje(message)
    
    async def obtenerPartida(self, partida_id: str):
        partida = await obtenerPartida(partida_id)
        return partida
