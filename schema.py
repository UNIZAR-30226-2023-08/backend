from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str 
    email: str | None = None
    real_name: str | None = None
    disabled: bool | None = False
    lp: int | None = None #Puntos de Liga
    coins: int | None = None


class UserInDB(User):
    hashed_password: str

