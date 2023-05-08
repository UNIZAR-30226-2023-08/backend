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
     partida = await dbPartida2Jugadores.find_one({'id': idP})
     partida_seleccionada = dict(partida) 
     return partida_seleccionada

async def obtenerEstadoPartida(partida_id):
     partida = await dbPartida2Jugadores.find_one({'id': partida_id})
     partida_seleccionada = dict(partida) 
     estado = partida_seleccionada["estado"]
     return estado

async def cambiar_estado_partida(partida_id, nuevo_estado):
     await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'estado': nuevo_estado}})

async def obtener_jugador_turno(partida_id):
     partida = await dbPartida2Jugadores.find_one({'id': partida_id})
     partida_seleccionada = dict(partida) 
     turno = partida_seleccionada["turno"]   
     return turno  
async def cambiar_jugador_turno(partida_id, turno):
     await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'turno': turno}})

async def cambiar_mazo_partida(partida_id, nuevo_mazo):
     await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'cartas': nuevo_mazo}})

async def obtener_mazo_partida(partida_id):
     partida = await dbPartida2Jugadores.find_one({'id': partida_id})
     partida_seleccionada = dict(partida) 
     cartas = partida_seleccionada["cartas"]   
     return cartas

async def cambiar_mano_jugador(partida_id, jugador, mano):
     if jugador == 0:
        await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'manoJ1': mano}})
     else:
        await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'manoJ2': mano}}) 

async def obtener_mano_jugador(partida_id, jugador):
     partida = await dbPartida2Jugadores.find_one({'id': partida_id})
     partida_seleccionada = dict(partida)
     if jugador == 0:
        mano = partida_seleccionada["manoJ1"]
     else:
        mano = partida_seleccionada["manoJ2"] 
     return mano

async def cambiar_triunfo_partida(partida_id, triunfo):
     await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'triunfo': triunfo}}) 

async def obtener_triufo_partida(partida_id):
     partida = await dbPartida2Jugadores.find_one({'id': partida_id})
     partida_seleccionada = dict(partida) 
     triunfo = partida_seleccionada["triunfo"]   
     return triunfo

async def cambiar_cartas_jugadas(partida_id, cartas_jugadas):
     await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'cartas_jugadas': cartas_jugadas}}) 

async def obtener_cartas_jugadas(partida_id):
     partida = await dbPartida2Jugadores.find_one({'id': partida_id})
     partida_seleccionada = dict(partida) 
     cartas_jugadas = partida_seleccionada["cartas_jugadas"]   
     return cartas_jugadas

async def cambiar_puntos_jugador(partida_id, puntos, jugador):
     if jugador == 0:
        await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'puntosJ1': puntos}})
     else:
        await dbPartida2Jugadores.update_one({'id': partida_id}, {'$set': {'puntosJ2': puntos}}) 


