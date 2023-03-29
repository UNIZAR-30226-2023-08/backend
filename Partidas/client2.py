import asyncio
import websockets

async def partida4(direccion):
    direccion = "ws://localhost:8000/partidaX/pepe"
    async with websockets.connect(direccion) as websocket:
        await websocket.send('PEPE  entra!')
        while(True):
            response = await websocket.recv()
            print(f'Respuesta recibida del servidor: {response}')
            
            if response == "Tu turno":
                await websocket.send('N: copa-12')
            elif response == "Arrastre":
                await websocket.send("C: copa-12, oro-12, espada-2, basto-3, oro-3, basto-5")
            
direccion = "ws://localhost:8000/partidaX/pepe"
asyncio.run(partida4(direccion))         




        