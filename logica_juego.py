
#Suma de puntos de la baza
def sumar_puntos(baza):
    #Recorrer la baza y sumar los puntos
    valores_cartas = {1: 11, 3: 10, 12: 4, 10: 3, 11: 2}
    puntos = 0
    for _, numCarta in baza:
        puntos += valores_cartas.get(numCarta, 0)
    return puntos

#Comprobar si la jugada es valida
def que_jugador_gana_baza(baza, triunfo):
    valorCarta = [2,4,5,6,7,11,10,12,3,1]
    cartaAlta = baza[0]
    for i in range(len(baza)):
        #Si son del mismo palo
        if cartaAlta[0] == baza[i][0]:
            valorCartaAlta = valorCarta.index(cartaAlta[1])
            valorCartaNueva = valorCarta.index(baza[i][1])
            if valorCartaAlta < valorCartaNueva:
                cartaAlta = baza[i]
        #Si no son del mismo palo
        else:
            #Si la nueva carta es del triunfo
            if baza[i][0] == triunfo:
                cartaAlta = baza[i]     
    return cartaAlta


def que_cartas_puede_usar_juagdor_arrastre(mano, baza, triunfo):
    if len(baza) == 1:
        return si_puedo_tengo_que_superar(mano, baza, triunfo)
    elif len(baza) == 2:
        cartaAlta = que_jugador_gana_baza(baza, triunfo)
        if cartaAlta != baza[0]:
            return si_puedo_tengo_que_superar(mano, baza, triunfo)
        else:
            return no_tengo_que_superar(mano, baza)
    elif len(baza) == 3:
        cartaAlta = que_jugador_gana_baza(baza, triunfo)
        if cartaAlta != baza[1]:
            return si_puedo_tengo_que_superar(mano, baza, triunfo)
        else:
            return no_tengo_que_superar(mano, baza)
        
                
def si_puedo_tengo_que_superar(mano, baza, triunfo):
    valorCarta = [2,4,5,6,7,11,10,12,3,1]
    cartasPosibles = []
    cartasPosiblesMayores = []
    cartasTriunfos = []
    palo = baza[0][0]
    if palo == triunfo:
        for x in range(len(mano)):
            if mano[x][0] == triunfo:
                cartasPosibles.append(mano[x])
            if len(cartasPosibles) == 0: return mano;
        for c in range(len(cartasPosibles)):
            cartasPosiblesValor = valorCarta.index(cartasPosibles[c][1])
            cartaBazaValor = valorCarta.index(baza[0][1])
            if cartasPosiblesValor > cartaBazaValor:
                cartasPosiblesMayores.append(cartasPosibles[c])
        if len(cartasPosiblesMayores) > 0: return cartasPosiblesMayores;
        else:return cartasPosibles;
    else:
        #Si no es triunfo 
        for x in range(len(mano)):
            if mano[x][0] == palo:
                cartasPosibles.append(mano[x])
        #Si tengo cartas del palo
        if len(cartasPosibles) > 0:
            for i in range(len(cartasPosibles)):
                cartasPosiblesValor = valorCarta.index(cartasPosibles[i][1])
                cartaBazaValor = valorCarta.index(baza[0][1])
                if cartasPosiblesValor > cartaBazaValor:
                    cartasPosiblesMayores.append(cartasPosibles[i])
            #Si tengo cartas de ese palo mayores
            if len(cartasPosiblesMayores) > 0: return cartasPosiblesMayores;
            #Si tengo cartas de ese palo pero no mayores
            else:return cartasPosibles;
        #Si no tengo cartas del palo ni trunfos juego lo que sea
        else:
            for x in range(len(mano)):
                if mano[x][0] == triunfo:
                    cartasTriunfos.append(mano[x])
            if len(cartasTriunfos) >= 0: return cartasTriunfos;
            else: return mano;

def no_tengo_que_superar(mano, baza):
    cartasPosibles = []
    palo = baza[0][0]
    for i in range(len(mano)):
        if mano[i][0] == palo:
            cartasPosibles.append(mano[i])
    if len(cartasPosibles) > 0: return cartasPosibles;
    else: return mano;
                

validez = que_cartas_puede_usar_juagdor_arrastre([("basto", 2), ("basto", 11), ("oro", 3)], [("copa", 5), ("basto", 4)], "espada")
print("       ")
print(validez)

suma = sumar_puntos([("espada", 3), ("espada", 1), ("basto", 5), ("oro", 5)])
#print(suma)

cartaGanadora = que_jugador_gana_baza([("espada", 3), ("espada", 1)], "oro")
#print(cartaGanadora)


         
                    
        