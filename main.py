from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from logica_juego import que_jugador_gana_baza, sumar_puntos

app = FastAPI()

connected_clients = {}
jugadores = 0

@app.websocket("/quierojugar2/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            print(f'Mensaje recibido del cliente {client_id}: {message}')
            connected_clients[client_id] = websocket
            if len(connected_clients) == 2:
                await send_to_all_clients("este es el nuevo socket", connected_clients)
            else:
                await websocket.send_text("esperando a otro jugador")
    except WebSocketDisconnect:
        del connected_clients[client_id]
        

async def send_to_all_clients(message: str, connected_clients: dict):
    newScoket = "/partida1/"
    print(newScoket)
    
    for websocket in connected_clients.values():
        try:
            await websocket.send_text(newScoket)
        except WebSocketDisconnect:
            pass
    new_partida(newScoket)

def new_partida(newScoket):
    @app.websocket(newScoket)
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive_text()
                print(message)
                #Aqui ya va toda la logica de recibo mano, veo que es, etc
                #Tengo que crear mano, y luego baza, y luego ver quien gana la baza
        except WebSocketDisconnect:
            print("adioas")

