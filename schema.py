from pydantic import BaseModel

#When you need to send data from a client (let's say, a browser) to your API, you send it as a request body.
#A request body is data sent by the client to your API. A response body is the data your API sends to the client.
#Your API almost always has to send a response body. But clients don't necessarily need to send request bodies all the time.
#To declare a request body, you use Pydantic models with all their power and benefits.
#https://fastapi.tiangolo.com/tutorial/body/

class Usuario(BaseModel):
    username: str
    nombre: str
    hashed_password: str
    correo: str
    disabled : bool 

    class Config:
        orm_mode = True
        
class Partida(BaseModel):
    id: str
    jugador1: str   
    jugador2: str
    jugador3: str   
    jugador4: str

    class Config:
        schema_extra = {
            "ejemplo": {
                "id": "1",
                "jugador1": "Jane Doe",
                "jugador2": "jdoe@example.com",
                "jugador3": "Experiments",
                "jugador4": "3.0",
            }
        }