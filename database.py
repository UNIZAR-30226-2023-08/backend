import motor 
import motor.motor_asyncio
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')
url = config.get('mongodb', 'url')

client = motor.motor_asyncio.AsyncIOMotorClient(url)
dbMongo  = client["guinote"]
dbPartida = dbMongo["partida"]
dbLogin = dbMongo["login"]


