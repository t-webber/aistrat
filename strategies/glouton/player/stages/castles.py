""" Gestion des château : construction et production """

from apis import connection
import player.logic.client_logic as cl

build_order = [connection.PAWN, connection.PAWN, connection.KNIGHT,
               connection.KNIGHT, connection.PAWN, connection.PAWN]


def move_peon_to_first_location(player, token, pawns, border, border_y, border_x):
    """construit le premier château """
    destination = (border, border) if player == "A" else (border_y, border_x)
    d = cl.distance_to_list(destination, pawns)
    # si d == 0, le pion est au bon endroit donc il va construire un château ici
    if d == 0:
        return

    for (y, x) in pawns:
        # ce pions est le plus proche de la bonne localisation
        if cl.distance(y, x, destination[0], destination[1]) == d:
            if player == "A":
                # assez proche de la destination en x : déplacement en y
                if x >= border:
                    connection.move(connection.PAWN, y, x, y +
                                    1, x, player, token)
                else:  # déplacement en x
                    connection.move(connection.PAWN, y, x, y,
                                    x+1, player, token)
            else:
                # assez proche de la destination en x : déplacement en y
                if x <= border_x:
                    connection.move(connection.PAWN, y, x, y -
                                    1, x, player, token)
                else:  # déplace en x
                    connection.move(connection.PAWN, y, x, y,
                                    x-1, player, token)
            pawns.remove((y, x))
            break


def build_castle(pawns, castles, player, token, gold, eknights):
    """ Construit des châteaux, et, au début, prend controle d'un péons pour construire le premier château au bon endroit  """
    len_y, len_x = connection.size_map()

    # définis les bordures pour ne pas y construire de château
    border = 2
    border_y = len_y - 1 - border
    border_x = len_x - 1 - border

    # adapte le côté au joueur : joueur A (haut gauche) ou joueur B (bas droite)

    # Si aucun château n'a été construit, prend le controle d'un pion, le met en (2,2) et ensuite construit un château
    if len(castles) == 0:
        move_peon_to_first_location(
            player, token, pawns, border, border_y, border_x)

    # Si il y a suffisemment de châteaux ou pas assez d'argent, n'essaie rien
    if len(castles) >= min(len_y, len_x) // 2 or gold < connection.PRICES[connection.CASTLE]:
        return

    # construit un château au premier moment où un pion est suffisemment loin des châteaux existants
    for pawn in pawns:
        y, x = pawn
        # distance au château le plus proche
        d = cl.distance_to_list((y, x), castles)

        # si le pions est suffisamment loin de la bordure
        if border <= x <= border_x and border <= y <= border_y and d >= 3 and not cl.exists_close(pawn, eknights, 2):
            connection.build(connection.CASTLE, y, x, player, token)
            pawns.remove(pawn)
            gold -= connection.PRICES[connection.CASTLE]
            return


def create_units(castles, player, token, eknight, knight, gold, defenders, nb_gold, nb_pawn, nb_fog):
    """ TLe château cree des unitées  """
    n = len(eknight) - len(knight)

    for (y, x) in castles:
        # Nous somme attaqués, production de défenseurs
        if build_order != []:
            suivant = build_order.pop()
            if gold > connection.PRICES[suivant]:
                connection.build(suivant, y, x, player, token)
                gold -= connection.PRICES[suivant]
            else:
                build_order.append(suivant)
        else:
            if n > 0:
                if gold > connection.PRICES[connection.KNIGHT]:
                    connection.build(connection.KNIGHT, y, x, player, token)
                    gold -= connection.PRICES[connection.KNIGHT]
                    defenders.append((y, x))
                    n -= 1

            # garder un équilibre entre defense et attaque et produire plus tôt
            elif gold > connection.PRICES[connection.KNIGHT] and (2 * len(knight) <= len(defenders) or len(knight) <= 2/3*nb_pawn):
                if connection.build(connection.KNIGHT, y, x, player, token):
                    gold -= connection.PRICES[connection.KNIGHT]

            # trop d'argent on achète des défenseurs
            elif gold > connection.PRICES[connection.KNIGHT] * 2 and len(castles) >= 2 and nb_pawn > 3:
                if connection.build(connection.KNIGHT, y, x, player, token):
                    gold -= connection.PRICES[connection.KNIGHT]

            # Pas assez d'argent, et de l'argent est disponible sur la carte (ou du brouillard de guerre)
            elif gold > connection.PRICES[connection.PAWN] * 1.25 and nb_gold + nb_fog > nb_pawn and len(knight) >= 2/3*nb_pawn:
                connection.build(connection.PAWN, y, x, player, token)
                gold -= connection.PRICES[connection.PAWN]
                nb_pawn += 1
