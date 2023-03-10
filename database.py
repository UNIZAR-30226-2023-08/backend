
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import motor 
import motor.motor_asyncio

DATABASE_URL = "mysql+mysqlconnector://root:mnltr321@localhost:3306/fastapi"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_database_session():
    try:
        db = SessionLocal()
        yield db

    finally:
        db.close()


MONGODB_URL = "mongodb+srv://lacnaru02sol:lacnaru02sol@guinote.6djqfmk.mongodb.net/?retryWrites=true&w=majority"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
dbMongo  = client["guinote"]
dbPartida = dbMongo["partida"]

