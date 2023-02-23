from datetime import date
from pydantic import BaseModel

#When you need to send data from a client (let's say, a browser) to your API, you send it as a request body.
#A request body is data sent by the client to your API. A response body is the data your API sends to the client.
#Your API almost always has to send a response body. But clients don't necessarily need to send request bodies all the time.
#To declare a request body, you use Pydantic models with all their power and benefits.
#https://fastapi.tiangolo.com/tutorial/body/

class Usuario(BaseModel):
    
    id: str
    nombre: str
    password: str
    
    class Config:
        orm_mode = True #will instruct Pydantic model to read the data as a dictionary and as an atribute
