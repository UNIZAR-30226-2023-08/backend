from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
from logica_juego import crear_mazo, repartir_cartas, que_jugador_gana_baza, sumar_puntos, que_cartas_puede_usar_jugador_arrastre
import random

#TODO almacenar nombre usuario juagdor

app = FastAPI()

sockets = {}
socket0_received = asyncio.Event()
socket1_received = asyncio.Event()
socket2_received = asyncio.Event()

message_socket = None

async def main_program():
    global message_socket
    while True:
        
        while len(sockets) < 3:
            await asyncio.sleep(1)
            
        
        puntosJugador0 = 0
        puntosJugador1 = 0
        puntosJugador2 = 0
        
        orden_inicial = [0,1,2]
        orden = [0,1,2]
                            
        manos = []
        triunfo, manos = await comienzo_partida()
        
        await send_message_to_all_sockets("Arrastre")
        
        for i in range(2):
            await mandar_manos(orden_inicial, manos)
            orden, manos, puntosJugador0, puntosJugador1, puntosJugador2 = await arrastre(
                orden_inicial, orden, triunfo, puntosJugador0, puntosJugador1, puntosJugador2, manos)
            
        if puntosJugador0 == puntosJugador1 or puntosJugador0 == puntosJugador2 or puntosJugador1 == puntosJugador2:
            mano_send = {"Perdedor": None, "0": puntosJugador0 ,"1": puntosJugador1, "2": puntosJugador2}
            message = json.dumps(mano_send)                        
            await send_message_to_all_sockets(message)
            break
        elif puntosJugador1 < puntosJugador0 < puntosJugador2  or puntosJugador2 < puntosJugador0 < puntosJugador1:
            mano_send = {"Perdedor": 0, "0": puntosJugador0 ,"1": puntosJugador1, "2": puntosJugador2}
            message = json.dumps(mano_send)                        
            await send_message_to_all_sockets(message)
            break
        elif puntosJugador0 < puntosJugador1 < puntosJugador2  or puntosJugador2 < puntosJugador1 < puntosJugador0:
            mano_send = {"Perdedor": 1, "0": puntosJugador0 ,"1": puntosJugador1, "2": puntosJugador2}
            message = json.dumps(mano_send)                        
            await send_message_to_all_sockets(message)
            break
        else:
            mano_send = {"Perdedor": 2, "0": puntosJugador0 ,"1": puntosJugador1, "2": puntosJugador2}
            message = json.dumps(mano_send)                        
            await send_message_to_all_sockets(message)
            break
                   


@app.websocket("/socket/0/{client_id}")
async def websocket_endpoint_socket1(websocket: WebSocket, client_id: str):
    global message_socket
    await websocket.accept()
    sockets["socket0"] = websocket  
    try:
        while True:
            message_socket = await websocket.receive_text()
            socket0_received.set()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        sockets.pop("socket0", None)

@app.websocket("/socket/1/{client_id}")
async def websocket_endpoint_socket2(websocket: WebSocket, client_id: str):
    global message_socket
    await websocket.accept()
    sockets["socket1"] = websocket  
    try:
        while True:
            message_socket = await websocket.receive_text()
            socket1_received.set()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        sockets.pop("socket1", None)
        
@app.websocket("/socket/2/{client_id}")
async def websocket_endpoint_socket2(websocket: WebSocket, client_id: str):
    global message_socket
    await websocket.accept()
    sockets["socket2"] = websocket  
    try:
        while True:
            message_socket = await websocket.receive_text()
            socket2_received.set()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        sockets.pop("socket2", None)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main_program())
    
async def send_message_to_all_sockets(message: str):
    for websocket in sockets.values():
        await websocket.send_text(message)
        
async def await_message(id: str):
    if id == "0":
        await socket0_received.wait()
        socket0_received.clear()
    elif id == "1":
        await socket1_received.wait()
        socket1_received.clear()
    else:
        await socket2_received.wait()
        socket2_received.clear()
        
async def send_message_to_socket(socketid: str, message: str):
    websocket = sockets.get("socket" + socketid)
    if websocket:
        await websocket.send_text(message)

async def comienzo_partida():
    mazo = crear_mazo()
    random.shuffle(mazo)
    
    mano1 = mazo[:len(mazo)//3]
    mano2 = mazo[len(mazo)//3:2*(len(mazo)//3)]
    mano3 = mazo[2*(len(mazo)//3):]
    triunfo = random.choice(mano3)
    mano3.remove(triunfo)
    
    manos = []
    manos.append(mano1)
    manos.append(mano2)
    manos.append(mano3)
    
    # Repartir manos a los jugadores
    for i in range(3):
        mano_send = {"Cartas": manos[i], "Triunfo": triunfo ,"Jugador": i}
        message = json.dumps(mano_send)
        await send_message_to_socket(str(i), message)
        
    return triunfo, manos

async def repartir(orden_inicial, mazo, triunfo, manos):
    for i in orden_inicial:
        if len(mazo) == 0:
            carta_robada = triunfo
        else:
            carta_robada = mazo[0]
            mazo.remove(carta_robada)
        manos[i].append(carta_robada)
        mano_send = manos[i]
        message = json.dumps(mano_send)
        await send_message_to_socket(str(i), message)
    
    return mazo, manos

async def arrastre(orden_inicial, orden, triunfo, puntosJugador0, puntosJugador1, puntosJugador2, manos):
    cartas_jugadas = [None, None, None]
    cartas_jugadas_mandar = [None, None, None]
    puntuacion_cartas = []
    global message_socket
    
    for i in range(3):
        #si eres el primero en tirar puedes usar lo que quieras
        if i == 0:
            print(cartas_jugadas)
            mano_send = {"0": cartas_jugadas_mandar[0], "1": cartas_jugadas_mandar[1], "2": cartas_jugadas_mandar[2] , "Turno": orden[i], "Triunfo": None}
            message = json.dumps(mano_send)
            await send_message_to_all_sockets(message)
            
            mano_send = manos[orden[i]]
            message = json.dumps(mano_send)
            await send_message_to_socket(str(orden[i]), message)
        else:
            mano_send = {"0": cartas_jugadas_mandar[0], "1": cartas_jugadas_mandar[1], "2": cartas_jugadas_mandar[2], "Turno": orden[i], "Triunfo": None}
            message = json.dumps(mano_send)
            await send_message_to_all_sockets(message)   
                     
            cartas_posibles = que_cartas_puede_usar_jugador_arrastre(manos[orden[i]], puntuacion_cartas, triunfo)
            message = json.dumps(cartas_posibles)
            await send_message_to_socket(str(orden[i]), message)
        
        await await_message(str(orden[i]))
        
        carta = message_socket
                 
        palo, valor = carta.split("-") 
        carta_tupla = (palo, int(valor))
                
        manos[orden[i]].remove(carta_tupla)
        cartas_jugadas[i] = carta_tupla
        cartas_jugadas_mandar[orden[i]] = carta_tupla
        puntuacion_cartas.append(carta_tupla)
        
    mano_send = {"0": cartas_jugadas_mandar[0], "1": cartas_jugadas_mandar[1], "2": cartas_jugadas_mandar[2], "Turno": orden[i], "Triunfo": None}
    message = json.dumps(mano_send)
    await send_message_to_all_sockets(message)
        
    carta_gandora = que_jugador_gana_baza(puntuacion_cartas, triunfo)
    indice_ganador = puntuacion_cartas.index(carta_gandora)
    
    #Sumo puntos al jugador que ha ganado la baza
    if orden[indice_ganador] == orden_inicial[0]:
        puntosJugador0 += sumar_puntos(cartas_jugadas)
        await send_message_to_all_sockets("Ganador: 0")
    elif orden[indice_ganador] == orden_inicial[1]:
        puntosJugador1 += sumar_puntos(cartas_jugadas)
        await send_message_to_all_sockets("Ganador: 1")
    else:
        puntosJugador2 += sumar_puntos(cartas_jugadas)
        await send_message_to_all_sockets("Ganador: 2")
    
    #Cambiar el orden si ha ganado el 1 o 2 la baza
    if indice_ganador == 1:
        orden = [orden[1],orden[2],orden[0]]
    elif indice_ganador == 2:
        orden = [orden[2],orden[0],orden[1]]
    
    return orden, manos, puntosJugador0, puntosJugador1, puntosJugador2

async def comprobarGanador(puntosJugador0, puntosJugador1):
    if puntosJugador1 >= 100:
        message = {"Ganador": 0, "0": puntosJugador0 ,"1": puntosJugador1}
        message = json.dumps(message)
        await send_message_to_all_sockets(message)
        return True
    elif puntosJugador1 >= 100:
        message = {"Ganador": 1, "0": puntosJugador0 ,"1": puntosJugador1}
        message = json.dumps(message)
        await send_message_to_all_sockets(message)
        return True
    else:
        return False

async def mandar_manos(orden_inicial, manos):
    for i in orden_inicial:
        mano_send = manos[i]
        message = json.dumps(mano_send)
        await send_message_to_socket(str(i), message)
    
