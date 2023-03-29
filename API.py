from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import random
from Partidas.partida2 import partida2
from Partidas.logica_juego import que_jugador_gana_baza, sumar_puntos
import asyncio

app = FastAPI()
global connected_clients_2
connected_clients_2 = {}
connected_clients_3 = {}
connected_clients_4 = {}





















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