""" Add castles when needed """

import api
import player.logic.client_logic as cl


def distance_2_castle(y_curr, x_curr, castles):
    """ Get the distance to the nearest castle """
    d = float('inf')
    for (y, x) in castles:
        d = min(cl.distance(y, x, y_curr, x_curr), d)
    return d


def check_build(pawns, castles, player, token, gold):
    """ Build some castle, and, at the beggining, take control of a pawn to build the first castle in the right place  """
    len_y, len_x = api.size_map()

    # définis les bordures pour ne pas y construire de château
    border = 2
    border_x = len_x - 1 - border
    border_y = len_y - 1 - border

    # adapte le côté au joueur : joueur A (haut gauche) ou joueur B (bas droite)
    good = (border, border) if player == "A" else (
        border_y, border_x)

    # Si aucun château n'a été construit, prend le controle d'un pion, le met en (2,2) et ensuite construit un château
    if len(castles) == 0:
        d = distance_2_castle(good[0], good[1], pawns)
        if d != 0:  # si d == 0, le pion est au bon endroit donc il va construire un château ici
            for (y, x) in pawns:

                # ce pions est le plus proche de la bonne localisation
                if cl.distance(y, x, good[0], good[1]) == d:
                    if player == "A":

                        # assez proche de la destination en x : déplacement en y
                        if x >= border:
                            api.move(api.PAWN, y, x, y +
                                     1, x, player, token)
                        else:  # déplacement en x
                            api.move(api.PAWN, y, x, y,
                                     x+1, player, token)
                    else:
                        # assez proche de la destination en x : déplacement en y
                        if x <= border_x:
                            api.move(api.PAWN, y, x, y -
                                     1, x, player, token)
                        else:  # déplace en x
                            api.move(api.PAWN, y, x, y,
                                     x-1, player, token)
                    pawns.remove((y, x))
                    break

    # Si il y a suffisemment de châteaux ou pas assez d'argent, n'essaie rien 
    if len(castles) >= min(len_y, len_x) // 2 or gold < api.PRICES[api.CASTLE]:
        return

    # construit un château au premier moment où un pion est suffisemment loin des châteaux existants
    for pawn in pawns:
        y, x = pawn
        d = distance_2_castle(y, x, castles)  # distance au château le plus proche

        # si le pions est suffisamment loin de la bordure
        if border <= x <= border_x and border <= y <= border_y and d >= 3:
            api.build(api.CASTLE, y, x, player, token)
            pawns.remove(pawn)
            gold -= api.PRICES[api.CASTLE]
            return


def create_pawns(castles, player, token, eknight, knight, gold, defenders, nb_gold, nb_pawn, nb_fog):
    """ The castles will spawn units here """
    n = len(eknight) - len(knight)

    for (y, x) in castles:
        # Nous somme attaqués, production de défenseurs 
        if n > 0:
            if gold > api.PRICES[api.KNIGHT]:
                api.build(api.KNIGHT, y, x, player, token)
                gold -= api.PRICES[api.KNIGHT]
                defenders.append((y, x))
                api.PRICES[api.KNIGHT] -= 1
                n -= 1

        # garder un equilibre entre defense et attaque et produire plus tôt
        elif gold> api.PRICES[api.KNIGHT] and (len(knight)<=(1/2*len(defenders)) or len(knight)<=2/3*len(defenders)):
            if api.build(api.KNIGHT, y, x, player, token):
                gold -= api.PRICES[api.KNIGHT]

        # trop d'argent on achète des défenseurs
        elif gold > api.PRICES[api.KNIGHT] * 2 and len(castles) >= 2:
            if api.build(api.KNIGHT, y, x, player, token):
                gold -= api.PRICES[api.KNIGHT]

        # Pas assez d'argent, et de l'argent est disponible sur la carte (ou du brouillard de guerre)
        elif gold > api.PRICES[api.PAWN] * 1.25 and nb_gold + nb_fog > nb_pawn and 2/3*len(defenders)<= len(knight):
            api.build(api.PAWN, y, x, player, token)
            gold -= api.PRICES[api.PAWN]
            nb_pawn += 1
