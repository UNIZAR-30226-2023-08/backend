from Database.database import dbLogin, dbPartida2, dbPartida3, dbPartida4, dbPartida2Jugadores, dbTienda
from  Database.schema import Partida2, Tienda, User

async def actualizarLP(jugador, puntos):
     dbLogin.update_one({'username': jugador}, {'$inc': {'lp': puntos}})

async def actualizarCoins(jugador, coins):
     dbLogin.update_one({'username': jugador}, {'$inc': {'coins': coins}})

async def actualizarVictorias(jugador):
     dbLogin.update_one({'username': jugador}, {'$inc': {'wonMatches': 1}})
     dbLogin.update_one({'username': jugador}, {'$inc': {'winStreak': 1}})

async def actualizaDerrotas(jugador):
     dbLogin.update_one({'username': jugador}, {'$inc': {'lostMatches': 1}})
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
     top_users = [{key: user[key] for key in user if key in ['username', 'lp', 'wonMatches', 'lostMatches','winStreak']} for user in top_users]
     return top_users

async def obtenerJugador(username: str):
     user = await dbLogin.find_one({"username": username})
     if user:
          user_seleccionado = {k: v for k, v in user.items() if k in ['username', 'lp', 'wonMatches', 'lostMatches', 'winStreak']}
          return user_seleccionado
     else:
          return None

async def obtenerBarajasTienda(username: str):
     user = await dbTienda.find_one({"username": username})
     if user:
          user_seleccionado = {k: v for k, v in user.items() if k in ['barajas']}
          lista_barajas_usuario = user_seleccionado['barajas']
          lista_barajas = await actualizarBarajasTienda(username, lista_barajas_usuario)
          return lista_barajas

     else:
          filename = "barajas.txt"
          tuplas = []
          with open(filename, "r") as file:
               for line in file:
                    line = line.strip()  # Eliminar saltos de línea y espacios en blanco al principio y final
                    str_value, int_value = line.split(",")  # Separar la cadena de texto y el entero
                    tuplas.append((str_value, int(int_value))) 
          tienda = Tienda(username= username, barajas=tuplas)
          datos_tienda = tienda.dict()
          dbTienda.insert_one(datos_tienda)
         
          return tuplas
async def actualizarBarajasTienda(username: str, tupla):
     filename = "barajas.txt"
     tuplas = []
     with open(filename, "r") as file:
          for line in file:
               line = line.strip()  # Eliminar saltos de línea y espacios en blanco al principio y final
               str_value, int_value = line.split(",")  # Separar la cadena de texto y el entero
               tuplas.append((str_value, int(int_value))) 
     for tupla2 in tuplas:
          encontrado = False
          for tupla1 in tupla:
               if tupla1[0] == tupla2[0]:
                    encontrado = True
                    break
          if not encontrado:
               tupla.append(tupla2)

     dbTienda.update_one({'username': username}, {'$set': {'barajas': tupla}})
     return tupla

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


