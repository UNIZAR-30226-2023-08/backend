# main.py


#TOD EN LA CARPETA DEL PROYECTO  // INSTALACIÓN
#python3 -m venv env
#pip3 install fastapi
#pip3 install "uvicorn[standard]"
#python -m uvicorn main:app --reload

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_database_session
import model 
from model import Usuario

model.Base.metadata.create_all(bind=engine)

app = FastAPI() #Crea una instancia de FastApi

@app.get("/") #Funcion que hay debajo de esta petición
async def root():
    return {"Hello world"}

def get_usuario_info_by_id(sesion: SessionLocal, id: str):
    return sesion.query(Usuario).filter(Usuario.id == id).first()

@app.get("/usuario/{usuario_id}")
async def root(usuario_id: str, sesion: Session = Depends(get_database_session)):
    
    usuario_info = get_usuario_info_by_id(sesion, usuario_id)
    return usuario_info
    


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
