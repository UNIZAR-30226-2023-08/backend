from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import random
import asyncio

from Partidas.logica_juego import crear_mazo, que_cartas_puede_usar_jugador_arrastre, que_jugador_gana_baza, repartir_cartas, sumar_puntos
from Partidas.ranking import COINS_GANADOR, LP_GANADOR, LP_PERDEDOR
from Database.crud import actualizaDerrotas, actualizarCoins, actualizarLP, actualizarVictorias, insertarPartida2
from Database.schema import PartidaDos

app = FastAPI()

players_connected = {}
jugadores = {}

puntosJugador1 = 0
puntosJugador2 = 0

#async def partida2(direccion, app):
#TODO hacer que sea una funcino que le llame el main    
@app.websocket("/partidaX/{client_id}") ##CLIENTE ID = USERNAME
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            print(f'Mensaje recibido del cliente {client_id}: {message}')
            players_connected[client_id] = websocket
            if len(players_connected) == 2:
                for modo in range(2):
                    #TODOD quitar este mensaje
                    await send_to_all_clients("se empieza", players_connected)
                    mazo, triunfo, jugadores_inicial, jugadores = await comienzo_partida(players_connected)
                    for i in range(14):
                        jugadores, puntosJugador1, puntosJugador2 = await ronda(jugadores_inicial, jugadores, players_connected, triunfo, puntosJugador1, puntosJugador2, websocket)
                        if modo == 2: 
                            if comprobarGanador(puntosJugador1, puntosJugador2): break
                        mazo =  await repartir(jugadores, mazo, triunfo)
                    
                    manos = await recibir_manos(websocket, players_connected)
                    for i in range(6):
                        #Comienza el arrastre
                        jugadores, manos, puntosJugador1, puntosJugador2 = await arrastre(websocket, jugadores_inicial, jugadores, players_connected, triunfo, puntosJugador1, puntosJugador2, manos)
                        if modo == 2: 
                            if comprobarGanador(puntosJugador1, puntosJugador2): break
                   
                    if puntosJugador1 > 100:
                        message = "Gana el jugador 1, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2)
                        await send_to_all_clients(message, players_connected)
                        break
                    elif puntosJugador2 > 100:
                        message = "Gana el jugador 2, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2)
                        await send_to_all_clients(message, players_connected)
                        break
                    else:
                        message = "Vueltas, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2)
                        await send_to_all_clients(message, players_connected)
                
                websocket.close()
                #TODO meter datos de partidas y puntos y esas cosas en la bd
                guardarBD()
                
            else:
                #TODO si se desconecta un jugador, que hacer
                await websocket.send_text("esperando a otro jugador")
            
        
    except WebSocketDisconnect:
        print("Exception")
        
async def comienzo_partida(players_connected):
    mazo = crear_mazo()
    random.shuffle(mazo)
    manos, mazo = repartir_cartas(mazo, 2)
    triunfo = mazo[0]
    mazo.remove(triunfo)
    jugadores = list(players_connected)
    jugadores_inicial = list(players_connected)
    
    # Repartir manos a los jugadores
    for i, player_id in enumerate(jugadores):
        mano_str = ', '.join([f"{palo}-{valor}" for palo, valor in manos[i]])
        triunfo_str = f"{triunfo[0]}-{triunfo[1]}"
        message = f"Mano: {mano_str}, Triunfo: {triunfo_str}, NumJugador: {i+1}"
        asyncio.create_task(send_to_single_client(player_id, message, players_connected))
        
    return mazo, triunfo, jugadores_inicial, jugadores
        
async def ronda(jugadores_inicial, jugadores, players_connected, triunfo, puntosJugador1, puntosJugador2, websocket):
    cartas_jugadas = []
    #Que cada jugador juegue una carta
    for i, player_id in enumerate(jugadores):
        message = f"Tu turno"
        asyncio.create_task(send_to_single_client(player_id, message, players_connected))
        carta = await websocket.receive_text()
        if carta[0] !=  "N":
            break
        palo, valor = carta.split("-")
        carta_tupla = (palo, int(valor))
        cartas_jugadas.append(carta_tupla)
        message = f"Jugada: {carta}"
        asyncio.create_task(send_to_all_clients(message, players_connected))
        
    carta_gandora = que_jugador_gana_baza(cartas_jugadas, triunfo)
    indice_ganador = cartas_jugadas.index(carta_gandora)
    
    #Sumo puntos al jugador que ha ganado la baza
    if jugadores[indice_ganador] == jugadores_inicial[0]:
        puntosJugador1 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 1", players_connected)
    else:
        puntosJugador2 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 2", players_connected)
    #Si el jugador que ha ganado es el 1, cambia el orden de los jugadores
    if indice_ganador == 1:
        jugadores = jugadores[1:] + jugadores[:1]
        
    return jugadores, puntosJugador1, puntosJugador2

#Repartir carta robada a los jugadores
async def repartir(jugadores, mazo, triunfo):
    for i, player_id in enumerate(jugadores):
        if len(mazo) == 0:
            carta_robada = triunfo
        else:
            carta_robada = mazo[0]
            mazo.remove(carta_robada)
        carta_str = f"{carta_robada[0]}-{carta_robada[1]}"
        message = f"Carta_robada: {carta_str}"
        asyncio.create_task(send_to_single_client(player_id, message, players_connected))
        
    return mazo


    
async def arrastre(websocket, jugadores_inicial, jugadores, players_connected, triunfo, puntosJugador1, puntosJugador2, manos):
    cartas_jugadas = []
    for i, player_id in enumerate(jugadores):
        #si eres el primero en tirar puedes usar lo que quieras
        if i == 0:
            mano_str = ', '.join([f"{palo}-{valor}" for palo, valor in manos[i]])
            message = f"Tu turno: {mano_str}"
            asyncio.create_task(send_to_single_client(player_id, message, players_connected))
        #sino eres el primero en tirar depenses de la baza
        else:
            cartas_posibles = que_cartas_puede_usar_jugador_arrastre(manos[i], cartas_jugadas, triunfo)
            cartas_posibles = ', '.join([f"{palo}-{valor}" for palo, valor in cartas_posibles[i]])
            message = f"Tu turno: {cartas_posibles}"
            asyncio.create_task(send_to_single_client(player_id, message, players_connected))
        carta = await websocket.receive_text()
        if carta[0] !=  "A":
            break
        #carta = "oro-1"
        palo, valor = carta.split("-")
        carta_tupla = (palo, int(valor))
        manos[i].remove(manos[i][0])
        cartas_jugadas.append(carta_tupla)
        message = f"Jugada: {carta}"
        asyncio.create_task(send_to_all_clients(message, players_connected))
        
    carta_gandora = que_jugador_gana_baza(cartas_jugadas, triunfo)
    indice_ganador = cartas_jugadas.index(carta_gandora)
    
    #Sumo puntos al jugador que ha ganado la baza
    if jugadores[indice_ganador] == jugadores_inicial[0]:
        puntosJugador1 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 1", players_connected)
    else:
        puntosJugador2 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 2", players_connected)
    #Si el jugador que ha ganado es el 1, cambia el orden de los jugadores
    if indice_ganador == 1:
        jugadores = jugadores[1:] + jugadores[:1]
        manos = manos[1:] + manos[:1]
    
    return jugadores, manos, puntosJugador1, puntosJugador2


async def send_to_all_clients(message: str, connected_clients: dict):
    for websocket in connected_clients.values():
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            pass
        
async def send_to_single_client(client_id: str, message: str, connected_clients: dict):
    websocket = connected_clients.get(client_id)
    
    if websocket is not None:
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            pass
    else:
        print(f"No se encontró el cliente con ID: {client_id}")
        
async def recibir_manos(websocket, players_connected):
    manos = []
    for i, player_id in enumerate(players_connected):
        await send_to_single_client(player_id, "Arrastre", players_connected)
        message = await websocket.receive_text()
        if message[0] != "C":
            break
        print(f"Mensaje recibido del cliente {player_id}: {message}")
        mano = []
        for carta in message.split(", "):
            palo, valor = carta.split("-")
            mano.append((palo, int(valor)))
        manos.append(mano)
    return manos

async def comprobarGanador(puntosJugador1, puntosJugador2):
    if puntosJugador1 >= 100:
        message = "Gana el jugador 1, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2)
        await send_to_all_clients(message, players_connected)
        return True
    elif puntosJugador2 >= 100:
        message = "Gana el jugador 2, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2)
        await send_to_all_clients(message, players_connected)
        return True
    else:
        return False

async def actualizarEstadisticas2Jugadores(jugadorGanador, jugadorPerdedor): #GANADOR, PERDEDOR
    await actualizarLP(jugadorGanador, LP_GANADOR)
    await actualizarCoins(jugadorGanador, COINS_GANADOR)
    await actualizarLP(jugadorPerdedor, LP_PERDEDOR)
    await actualizarVictorias(jugadorGanador)
    await actualizaDerrotas(jugadorPerdedor)
    
async def guardarPartida2Jugadores(puntosJugador1, puntosJugador2, jugadorGanador, jugadorPerdedor):  
      now = datetime.now().replace(second=0)
      formatted_date = now.strftime('%Y-%m-%d %H:%M')
      partida = PartidaDos(
          jugador1=jugadorGanador,
          jugador2=jugadorPerdedor,
          puntosJ1=puntosJugador1,
          puntosJ2=puntosJugador2,
          ganador=jugadorGanador,
          fecha=formatted_date
      )
      partida2 = partida.dict()
      await insertarPartida2(partida2)

