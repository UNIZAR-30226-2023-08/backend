import asyncio
import websockets

async def partida2(direccion):
    direccion = "ws://localhost:8000/partida/2/jose"
    async with websockets.connect(direccion) as websocket:
        await websocket.send('JOSE  entra!')
        while(True):
            response = await websocket.recv()
            print(f'Respuesta recibida del servidor: {response}')
        
            
direccion = "ws://localhost:8000/partidaX/pepe"
asyncio.run(partida2(direccion))         




        