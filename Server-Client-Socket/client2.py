import asyncio
import websockets

async def nuevaPartida(direccion):
    direccion = "ws://localhost:8000" + direccion
    async with websockets.connect(direccion) as websocket:
        await websocket.send('estoy en la nueva partida!')
        while(True):
            response = await websocket.recv()
            print(f'Respuesta recibida del servidor: {response}')

async def hello():
    async with websockets.connect('ws://localhost:8000/quierojugar2/pepe') as websocket:
        await websocket.send('Hola, servidor!')
        response = await websocket.recv()
        print(f'Respuesta recibida del servidor: {response}')
        
        if response == "esperando a otro jugador":
            response = await websocket.recv()
            print(f'Respuesta recibida del servidor: {response}')
            await nuevaPartida(response.strip())
        else:
            await nuevaPartida(response.strip())
            
                

asyncio.get_event_loop().run_until_complete(hello())



        