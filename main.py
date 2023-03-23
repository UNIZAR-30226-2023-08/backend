# main.py
#TOD EN LA CARPETA DEL PROYECTO  // INSTALACIÓN
#python3 -m venv env
#pip3 install fastapi
#pip3 install "uvicorn[standard]"
#python -m uvicorn main:app --reload

from datetime import timedelta, datetime
from fastapi import Body, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from jose import JWTError, jwt #pip install "python-jose[cryptography]"

from passlib.context import CryptContext #pip install "passlib[bcrypt]"
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_database_session
import model 
from model import Usuario
from pydantic import BaseModel
from database import dbMongo, dbPartida
from schema import Partida, Usuario
import schema
import model

model.Base.metadata.create_all(bind=engine)

app = FastAPI() #Crea una instancia de FastApi


#////////////////////////SECURITY FAST-API/////////////////////////
#https://fastapi.tiangolo.com/es/tutorial/security/

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    nombre: str
    correo: str
    disabled : bool 

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    usuario_info = comprobar_usuario(db, username)
    if usuario_info is None:
        pass
    else:
        return usuario_info
        
def comprobar_usuario(sesion: SessionLocal, username: str):
    return sesion.query(model.Usuario).filter(model.Usuario.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), sesion: Session = Depends(get_database_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(sesion, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: model.Usuario = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/login", response_model=Token )
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), sesion: Session = Depends(get_database_session)):
    user = authenticate_user(sesion, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=Usuario)
async def read_users_me(current_user: model.Usuario = Depends(get_current_active_user)):
    current_user.hashed_password = "****************"
    return current_user


#//////////////////////SECURITY//////////////////////////////////////////////////////


@app.get("/") #Funcion que hay debajo de esta petición
async def root():
    return {"TONTO EL QUE LO LEA"}

#Registra un nuevo usuario en la base de datos con contraseña cifrada
@app.post("/register", response_description="Aniadir nuevo usuario")
async def resgistrar_usuario(usuario: schema.Usuario, sesion: Session = Depends(get_database_session)):
    usuario.hashed_password = get_password_hash(usuario.hashed_password)
    nuevo_usuario = model.Usuario(**usuario.dict())
    sesion.add(nuevo_usuario)
    sesion.commit()
    sesion.refresh(nuevo_usuario) 

#Crea una partida en la base de datos mongodb (Incompleto)
@app.post("/crearPartida", response_description="Nueva partida", response_model=Partida) #Especifica valor a retornar
async def crear_partida(partida: schema.Partida):
    partida = jsonable_encoder(partida)
    nueva_partida = await dbPartida.insert_one(partida)
    return nueva_partida


######################################################
#################BASE DE DATOS########################
######################################################
#Instalar SQLAlchemy ORM objejct relational mapper
#pip install sqlalchemy mysql-connector-python

##INSTALAR Mysql 
##CREATE DATABASE fastapi

#Crear archivo database.py

####CREAR DATABASE MODEL -->  model.py
#cada atributo de la base de datos esta representado por una Column en SQLAlchemy

####CREAR DATABASE SQUEMA --> schema.py
#Leera los datos y los devolvera from API
#Para ello se creara un Pydantic schema para nuestro modelo
