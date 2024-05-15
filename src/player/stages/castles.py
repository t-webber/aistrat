""" Gestion des château : construction et production """

from apis import connection
import player.logic.client_logic as cl
from apis.kinds import Pawn, Knight


build_order = [connection.PAWN, connection.PAWN, connection.KNIGHT,
               connection.KNIGHT, connection.PAWN, connection.PAWN]


def move_peon_to_first_location(player, border, border_y, border_x):
    """construit le premier château """
    destination = (border, border) if player == "A" else (border_y, border_x)
    d = cl.distance_to_list(destination, player.pawns)
    # si d == 0, le pion est au bon endroit
    # donc il va construire un château ici
    if d == 0:
        return

    for pawn in player.pawns:
        # ce pions est le plus proche de la bonne localisation
        if cl.distance(pawn.y, pawn.x, destination[0], destination[1]) == d:
            if player == "A":
                # assez proche de la destination en x : déplacement en y
                if pawn.x >= border:
                    pawn.move(pawn.y + 1, pawn.x)
                else:  # déplacement en x
                    pawn.move(pawn.y, pawn.x+1)
            else:
                # assez proche de la destination en x : déplacement en y
                if pawn.x <= border_x:
                    pawn.move(pawn.y - 1, pawn.x)
                else:  # déplace en x
                    pawn.move(pawn.y, pawn.x - 1)
            break


def build_castle(player):
    """ 
    Construit des châteaux, et, au début, prend controle d'un péons 
    pour construire le premier château au bon endroit  
    """
    len_y, len_x = connection.size_map()

    # définis les bordures pour ne pas y construire de château
    border = 2
    border_y = len_y - 1 - border
    border_x = len_x - 1 - border

    # adapte le côté au joueur
    # - joueur A (haut gauche)
    # - joueur B (bas droite)

    # Si aucun château n'a été construit, prend le controle d'un pion,
    # le met en (2,2) et ensuite construit un château
    if len(player.castles) == 0:
        move_peon_to_first_location(
            player, border, border_y, border_x)

    # Si il y a suffisemment de châteaux ou pas assez d'argent, n'essaie rien
    if len(player.castles) >= min(len_y, len_x) // 2 or player.gold < connection.PRICES[connection.CASTLE]:
        return

    # construit un château au premier moment où un pion est suffisemment loin des châteaux existants
    for pawn in player.pawns:
        y, x = pawn
        # distance au château le plus proche
        d = cl.distance_to_list((y, x), player.castles)

        # si le pions est suffisamment loin de la bordure
        if border <= x <= border_x and border <= y <= border_y and d >= 3 and not cl.exists_close(pawn, player.eknights, 2):
            connection.build(connection.CASTLE, y, x, player, player.token)
            cl.find_unit(player.pawns, y, x)
            player.gold -= connection.PRICES[connection.CASTLE]
            return


def create_units(player):
    """ Création des unités par le château  """
    n = len(player.eknights) - len(player.defense) - len(player.attack)
    nb_pawn = len(player.pawns)

    for (y, x) in player.castles:
        # Nous somme attaqués, production de défenseurs
        if build_order:
            suivant = build_order.pop()
            if player.gold > connection.PRICES[suivant]:
                connection.build(suivant, y, x, player.id, player.token)
                player.gold -= connection.PRICES[suivant]
            else:
                build_order.append(suivant)
        else:
            if n > 0:
                if player.gold > connection.PRICES[connection.KNIGHT]:
                    connection.build(connection.KNIGHT, y, x,
                                     player.id, player.token)
                    player.gold -= connection.PRICES[connection.KNIGHT]
                    player.defenders.append(Knight(y, x, player))
                    n -= 1

            # garder un équilibre entre defense et attaque et produire plus tôt
            elif player.gold > connection.PRICES[connection.KNIGHT] and (2 * len(player.knight) <= len(player.defenders) or len(player.knight) <= 2/3*nb_pawn):
                if connection.build(connection.KNIGHT, y, x, player.id, player.token):
                    player.gold -= connection.PRICES[connection.KNIGHT]

            # trop d'argent on achète des défenseurs
            elif player.gold > connection.PRICES[connection.KNIGHT] * 2 and len(player.castles) >= 2 and nb_pawn > 3:
                if connection.build(connection.KNIGHT, y, x, player.id, player.token):
                    player.gold -= connection.PRICES[connection.KNIGHT]

            # Pas assez d'argent, et de l'argent est disponible sur la carte (ou du brouillard de guerre)
            elif player.gold > connection.PRICES[connection.PAWN] * 1.25 and len(player.good_player.gold) + len(player.bad_player.gold) + len(player.fog) > nb_pawn and len(player.knight) >= 2/3*nb_pawn:
                connection.build(connection.PAWN, y, x,
                                 player.id, player.token)
                player.gold -= connection.PRICES[connection.PAWN]
