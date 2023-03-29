def encontrar_intermedio(puntosJugador1, puntosJugador2, puntosJugador3):
    if puntosJugador1 >= puntosJugador2 >= puntosJugador3 or puntosJugador3 >= puntosJugador2 >= puntosJugador1:
        return puntosJugador2
    elif puntosJugador2 >= puntosJugador1 >= puntosJugador3 or puntosJugador3 >= puntosJugador1 >= puntosJugador2:
        return puntosJugador1
    else:
        return puntosJugador3
    
print(encontrar_intermedio(10, 20, 30))
