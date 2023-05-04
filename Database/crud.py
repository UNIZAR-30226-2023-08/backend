from Database.database import dbLogin, dbPartida2, dbPartida3, dbPartida4, dbPartida2Jugadores
from  Database.schema import Partida2

async def actualizarLP(jugador, puntos):
     dbLogin.update_one({'username': jugador}, {'$inc': {'lp': puntos}})

async def actualizarCoins(jugador, coins):
     dbLogin.update_one({'username': jugador}, {'$inc': {'coins': coins}})

async def actualizarVictorias(jugador):
     dbLogin.update_one({'username': jugador}, {'$inc': {'winMatches': 1}})
     dbLogin.update_one({'username': jugador}, {'$inc': {'winStreak': 1}})

async def actualizaDerrotas(jugador):
     dbLogin.update_one({'username': jugador}, {'$inc': {'looseMatches': 1}})
     dbLogin.update_one({'username': jugador}, {'$set': {'winStreak': 0}})

##///////GUARDAR PARTIDAS ACABADAS //////////////////////

async def insertarPartida2(partida2):
     dbPartida2.insert_one(partida2)

async def insertarPartida3(partida3):
     dbPartida3.insert_one(partida3)

async def insertarPartida4(partida4):
     dbPartida4.insert_one(partida4)

##////////////////////////////////////////////////////////
async def obtenerTopJugadoresRanking(limite: int):
     top_users = await dbLogin.find().sort("lp", -1).limit(limite).to_list(length=limite)
     top_users = [{key: user[key] for key in user if key in ['username', 'lp', 'winMatches', 'looseMatches']} for user in top_users]
     return top_users

##/////////////////////PARTIDA 2 JUGADORES ///////////////////////

async def insertarPartida2Jugadores(partida2):
     dbPartida2Jugadores.insert_one(partida2)

async def buscarPartida2Jugadores(jugador):
     partida = await dbPartida2Jugadores.find_one({'$or': [{'jugador1': None}, {'jugador2': None}]})
     if partida:
        # Se encontró una partida con un jugador a null, seleccionarla
        partida_seleccionada = dict(partida)
        partida_seleccionada["jugador2"] = jugador
        id = partida_seleccionada["id"]
        await dbPartida2Jugadores.update_one({"id": id},{"$set": {"jugador2": jugador}})

        return partida_seleccionada
     else:
        
        return None
     
async def buscarPartidaEmpezada(jugador):
     # Construct the query
     query = {"$or": [{"jugador1": jugador}, {"jugador2": jugador}]}
     partida = await dbPartida2Jugadores.find_one(query)

     if partida:
          partida_seleccionada = dict(partida)
          id_partida = partida_seleccionada["id"]
          return id_partida
     else:
          return None

async def obtenerPartida(idP):
     # Construct the query
     query = {{"idPartida": idP}}
     partida = await dbPartida2Jugadores.find_one(query)
     partida_seleccionada = dict(partida) 
     return partida_seleccionada