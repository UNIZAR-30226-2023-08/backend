from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from logica_juego import crear_mazo, repartir_cartas, que_jugador_gana_baza, sumar_puntos, que_cartas_puede_usar_jugador_arrastre
import random
import asyncio

app = FastAPI()

players_connected = {}
jugadores = {}

puntosEquipo1 = 0
puntosEquipo2 = 0

#async def partida4(direccion, app):
#TODO hacer que sea una funcino que le llame el main    
@app.websocket("/partidaX/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            print(f'Mensaje recibido del cliente {client_id}: {message}')
            players_connected[client_id] = websocket
            if len(players_connected) == 1:
                for modo in range(2):
                    #TODOD quitar este mensaje
                    await send_to_all_clients("se empieza", players_connected)
                    mazo, triunfo, jugadores_inicial, jugadores = await comienzo_partida(players_connected)
                    for i in range(4):
                        jugadores, puntosEquipo1, puntosEquipo2 = await ronda(jugadores_inicial, jugadores, players_connected, triunfo, puntosEquipo1, puntosEquipo2, websocket)
                        if modo == 2: 
                            if comprobarGanador(puntosEquipo1, puntosEquipo2): break
                        mazo =  await repartir(jugadores, mazo, triunfo)
                    
                    manos = await recibir_manos(websocket, players_connected)
                    for i in range(6):
                        #Comienza el arrastre
                        jugadores, manos, puntosEquipo1, puntosEquipo2 = await arrastre(websocket, jugadores_inicial, jugadores, players_connected, triunfo, puntosEquipo1, puntosEquipo2, manos)
                        if modo == 2: 
                            if comprobarGanador(puntosEquipo1, puntosEquipo2): break
                   
                    if puntosEquipo1 > 100:
                        message = "Gana el jugador 1, 3, Puntos 1 y 3: " + str(puntosEquipo1) + " , Puntos 2 y 4: " + str(puntosEquipo2)
                        await send_to_all_clients(message, players_connected)
                        break
                    elif puntosEquipo2 > 100:
                        message = "Gana el jugador 2, 4, Puntos 1 y 3: " + str(puntosEquipo1) + " , Puntos 2 y 4: " + str(puntosEquipo2)
                        await send_to_all_clients(message, players_connected)
                        break
                    else:
                        message = "Vueltas, Puntos 1 y 3: " + str(puntosEquipo1) + " , Puntos 2 y 4: " + str(puntosEquipo2)
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
    manos, mazo = repartir_cartas(mazo, 4)
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
        
async def ronda(jugadores_inicial, jugadores, players_connected, triunfo, puntosEquipo1, puntosEquipo2, websocket):
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
    if jugadores[indice_ganador] == jugadores_inicial[0] or jugadores[indice_ganador] == jugadores_inicial[2]:
        puntosEquipo1 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 1, 3", players_connected)
    else:
        puntosEquipo2 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 2, 4", players_connected)

    #Cambia el orden de los jugadores
    if indice_ganador == 1:
        jugadores = jugadores[1] + jugadores[2] + jugadores[3] + jugadores[0]	
    elif indice_ganador == 2:
        jugadores = jugadores[2] + jugadores[3] + jugadores[0] + jugadores[1]
    elif indice_ganador == 3:
        jugadores = jugadores[3] + jugadores[0] + jugadores[1] + jugadores[2]
        
    return jugadores, puntosEquipo1, puntosEquipo2

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


    
async def arrastre(websocket, jugadores_inicial, jugadores, players_connected, triunfo, puntosEquipo1, puntosEquipo2, manos):
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
    if jugadores[indice_ganador] == jugadores_inicial[0] or jugadores[indice_ganador] == jugadores_inicial[2]:
        puntosEquipo1 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 1, 3", players_connected)
    else:
        puntosEquipo2 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 2, 4", players_connected)

    #Cambia el orden de los jugadores
    if indice_ganador == 1:
        jugadores = jugadores[1] + jugadores[2] + jugadores[3] + jugadores[0]	
    elif indice_ganador == 2:
        jugadores = jugadores[2] + jugadores[3] + jugadores[0] + jugadores[1]
    elif indice_ganador == 3:
        jugadores = jugadores[3] + jugadores[0] + jugadores[1] + jugadores[2]
    
    return jugadores, manos, puntosEquipo1, puntosEquipo2


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

async def comprobarGanador(puntosEquipo1, puntosEquipo2):
    if puntosEquipo1 >= 100:
        message = "Gana el jugador 1 y 3, Puntos 1 y 3: " + str(puntosEquipo1) + " , Puntos 2 y 4: " + str(puntosEquipo2)
        await send_to_all_clients(message, players_connected)
        return True
    elif puntosEquipo2 >= 100:
        message = "Gana el jugador 2 y 4, Puntos 1 y 3: " + str(puntosEquipo1) + " , Puntos 2 y 4: " + str(puntosEquipo2)
        await send_to_all_clients(message, players_connected)
        return True
    else:
        return False


