import asyncio
import random
from Database.schema import Partida2
from Database.database import dbPartida2Jugadores
import uuid
from typing import List
from fastapi import WebSocket
from pydantic import BaseModel
import json

from Database.crud import cambiar_cartas_jugadas, cambiar_estado_partida, cambiar_jugador_turno, cambiar_mano_jugador, cambiar_mazo_partida, cambiar_puntos_jugador, cambiar_triunfo_partida, insertarPartida2Jugadores, obtener_cartas_jugadas, obtener_jugador_turno, obtener_mano_jugador, obtener_triufo_partida, obtenerEstadoPartida
from Database.crud import buscarPartida2Jugadores
from Database.crud import buscarPartidaEmpezada
from Database.crud import obtenerPartida
from modelo_guinote.logica_juego import crear_mazo, repartir_cartas


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
        message = json.dumps(message)
        socket_j1 = self.jugadores[0][1]
        socket_j2 = self.jugadores[2][1]
        await socket_j1.send_text(message)
        await socket_j2.send_text(message)

class PartidaManager:
    def __init__(self):
        self.partidas = {}

    async def connect(self, websocket: WebSocket, partida_id: str, username: str):
        await websocket.accept()
        await self.unirse_partida(websocket, partida_id, username)
        ##await self.enviar_mensaje(partida_id, f"{username} se ha unido a la partida.")

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
        if len(partida.jugadores) == 2:
            await self.cambiarEstadoPartida(partida_id, "DOS")
        partida.agregar_jugador(username, websocket)

    async def obtener_jugadores_partida(self, partida_id: str):
        if partida_id in self.partidas:
            return len(self.partidas[partida_id].jugadores)
        else:
            return 0

    async def eliminar_jugador(self, websocket: WebSocket, partida_id: str, username: str):
        if partida_id in self.partidas:
            partida = self.partidas[partida_id]
            partida.eliminar_jugador(websocket)
    
    async def obtenerPartida(self, partida_id: str):
        partida = await obtenerPartida(partida_id)
        return partida
    
    async def obtenerEstadoPartida(self, partida_id: str):
        estado = await obtenerEstadoPartida(partida_id)
        return estado
    
    async def cambiarEstadoPartida(self, partida_id: str, estado_siguiente: str):
        await cambiar_estado_partida(partida_id, estado_siguiente)

    async def cambiar_jugador_turno(self, partida_id: str):
        turno = await obtener_jugador_turno(partida_id)
        if turno == 0:
            await cambiar_jugador_turno(partida_id, 1)
        else:
            await cambiar_jugador_turno(partida_id, 0)
       
    async def obtener_turno(self, partida_id: str):
        turno = await obtener_jugador_turno(partida_id)
        return turno
    
    async def obtener_jugador_turno(self, partida_id: str):
        turno = await obtener_jugador_turno(partida_id)
        turno = turno + 1
        if partida_id in self.partidas:
            partida = self.partidas[partida_id]
            jugador = partida.jugadores[turno][0]
        return jugador
    
    async def obtener_mano_jugador(self, partida_id, jugador):
        if partida_id in self.partidas:
            partida = self.partidas[partida_id]
            if partida.jugadores[0][0] == jugador:
                mano = await obtener_mano_jugador(partida_id, 0)
            else:
                mano = await obtener_mano_jugador(partida_id, 1)
        return mano
    
    async def cambiar_mano_jugador(self, partida_id, jugador, mano):
        if partida_id in self.partidas: 
            partida = self.partidas[partida_id]
            if partida.jugadores[0][0] == jugador:
                await cambiar_mano_jugador(partida_id, 0, mano)
            else:
                await cambiar_mano_jugador(partida_id, 1, mano)

    async def obtener_triunfo_partida(self, partida_id):
        triunfo = await obtener_triufo_partida(partida_id)
        return triunfo 
    
    async def cambiar_cartas_jugadas(self, partida_id, cartas_jugadas):
        await cambiar_cartas_jugadas(partida_id, cartas_jugadas)

    async def obtener_cartas_jugadas(self, partida_id):
        cartas_jugadas = await obtener_cartas_jugadas(partida_id)
        return cartas_jugadas
    
    async def enviar_mensaje(self, mensaje, socket):
        message = json.dumps(mensaje)
        await socket.send_text(message)
    
    async def enviar_mensaje_todos(self, partida_id, message):
        if partida_id in self.partidas:
            partida = self.partidas[partida_id]
            await partida.enviar_mensaje(message)

    async def esperar_mensaje(self, socket):
        try:
            mensaje_jugador = await asyncio.wait_for(socket.receive_text(), timeout=60)
            return mensaje_jugador
        except asyncio.TimeoutError:
           print("SE FUE")
    
    async def cambiar_puntos_jugador(self, partida_id, puntos, jugador):
        await cambiar_puntos_jugador(partida_id, puntos, jugador)

    async def comenzar_partida(self, partida_id: str):
        manos = []
        mazo = crear_mazo()
        random.shuffle(mazo)
        manos, mazo = repartir_cartas(mazo, 2)
        triunfo = mazo[0]
        mazo.remove(triunfo)

        await cambiar_mazo_partida(partida_id, mazo)
        await cambiar_mano_jugador(partida_id, 0, manos[0])
        await cambiar_mano_jugador(partida_id, 1, manos[1])
        await cambiar_triunfo_partida(partida_id, triunfo)

    

