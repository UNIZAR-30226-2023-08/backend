from Database.database import dbLogin, dbPartida2, dbPartida3, dbPartida4

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

async def insertarPartida2(partida2):
     dbPartida2.insert_one(partida2)

async def insertarPartida3(partida3):
     dbPartida3.insert_one(partida3)

async def insertarPartida4(partida4):
     dbPartida4.insert_one(partida4)