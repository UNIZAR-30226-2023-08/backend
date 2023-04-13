from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from logica_juego import crear_mazo, que_jugador_gana_baza, sumar_puntos, que_cartas_puede_usar_jugador_arrastre
import random
import asyncio

#TODO quitar esto y las cartas recibidas simuladas
app = FastAPI()

players_connected = {}
jugadores = {}

puntosJugador1 = 0
puntosJugador2 = 0
puntosJugador3 = 0

#async def partida3(direccion, app):
#TODO hacer que sea una funcino que le llame el main    
@app.websocket("/partidaX/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            print(f'Mensaje recibido del cliente {client_id}: {message}')
            players_connected[client_id] = websocket
            if len(players_connected) == 3:
                await send_to_all_clients("se empieza", players_connected)
                manos, triunfo, jugadores_inicial, jugadores = await comienzo_partida(players_connected)
                
                for i in range(13):
                    #Comienza el arrastre
                    jugadores, manos = await arrastre(websocket, jugadores_inicial, jugadores, players_connected, triunfo, puntosJugador1, puntosJugador2, manos)


                if puntosJugador1 >= puntosJugador2 >= puntosJugador3 or puntosJugador3 >= puntosJugador2 >= puntosJugador1:
                    message = "Perdedor: 1, Ganador: 2, 3, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2) + " , Puntos3: " + str(puntosJugador3)
                    await send_to_all_clients(message, players_connected)
                elif puntosJugador2 >= puntosJugador1 >= puntosJugador3 or puntosJugador3 >= puntosJugador1 >= puntosJugador2:
                    message = "Perdedor: 2, Ganador: 1, 3, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2) + " , Puntos3: " + str(puntosJugador3)
                    await send_to_all_clients(message, players_connected)
                else:
                    message = "Perdedor: 3, Ganador: 1, 2, Puntos1: " + str(puntosJugador1) + " , Puntos2: " + str(puntosJugador2) + " , Puntos3: " + str(puntosJugador3)
                    await send_to_all_clients(message, players_connected)

                websocket.close()
                
                #TODO meter datos de partidas y puntos y esas cosas en la bd
                guardarBD()
                
            else:
                #TODO capturar las excepciones
                await websocket.send_text("esperando a otro jugador")
            
        
    except WebSocketDisconnect:
        print("Exception")
        
async def comienzo_partida(players_connected):
    mazo = crear_mazo()
    random.shuffle(mazo)
    
    mano1 = mazo[:len(mazo)//3]
    mano2 = mazo[len(mazo)//3:2*(len(mazo)//3)]
    mano3 = mazo[2*(len(mazo)//3):]
    triunfo = random.choice(mano3)
    mano3.remove(triunfo)
    
    jugadores = list(players_connected)
    jugadores_inicial = list(players_connected)
    manos = []
    manos.append(mano1)
    manos.append(mano2)
    manos.append(mano3)
    
    # Repartir manos a los jugadores
    for i, player_id in enumerate(jugadores):
        mano_str = ', '.join([f"{palo}-{valor}" for palo, valor in manos[i]])
        triunfo_str = f"{triunfo[0]}-{triunfo[1]}"
        message = f"Mano: {mano_str}, Triunfo: {triunfo_str}, NumJugador: {i+1}"
        asyncio.create_task(send_to_single_client(player_id, message, players_connected))
        
    return manos, triunfo, jugadores_inicial, jugadores

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
        carta = "oro-1"
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
    elif jugadores[indice_ganador] == jugadores_inicial[1]:
        puntosJugador2 += sumar_puntos(cartas_jugadas)
        await send_to_all_clients("Ganador_Baza: 2", players_connected)
    else:
        puntosJugador3 += sumar_puntos(cartas_jugadas)
        
    #Cambia el orden de los jugadores
    if indice_ganador == 1:
        jugadores = jugadores[1] + jugadores[2] + jugadores[0]
    elif indice_ganador == 2:
        jugadores = jugadores[2] + jugadores[0] + jugadores[1]
    
    return jugadores, manos



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
        

def guardarBD():
    #Guardo los datos en la BD
    print("Guardar datos en la BD")

