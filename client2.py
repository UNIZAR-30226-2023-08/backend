import asyncio
import websockets

async def partida4(direccion):
    direccion = "ws://localhost:8000/partidaX/pepe"
    async with websockets.connect(direccion) as websocket:
        await websocket.send('PEPE  entra!')
        while(True):
            response = await websocket.recv()
            print(f'Respuesta recibida del servidor: {response}')
            

            
direccion = "ws://localhost:8000/partidaX/pepe"
asyncio.run(partida4(direccion))         




        