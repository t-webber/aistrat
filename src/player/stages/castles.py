"""Gestion des château : construction et production."""


from __future__ import annotations
from typing import TYPE_CHECKING

from apis import connection, consts
from apis.kinds import Knight, Pawn
import player.logic.client_logic as cl

if TYPE_CHECKING:
    from apis.players import Player


build_order = [consts.PAWN, consts.PAWN, consts.KNIGHT,
               consts.KNIGHT, consts.PAWN, consts.PAWN]


def move_peon_to_first_location(player: Player, border: int, border_y: int, border_x: int):
    """Construit le premier château."""
    destination = (border, border) if player == "A" else (border_y, border_x)
    d = cl.distance_to_list(destination, player.pawns)
    # si d == 0, le pion est au bon endroit
    # donc il va construire un château ici
    if not d:
        return

    for pawn in player.pawns:
        # ce pions est le plus proche de la bonne localisation
        if cl.distance(pawn.y, pawn.x, destination[0], destination[1]) == d:
            if player == "A":
                # assez proche de la destination en x : déplacement en y
                if pawn.x >= border:
                    pawn.move(pawn.y + 1, pawn.x)
                else:  # déplacement en x
                    pawn.move(pawn.y, pawn.x + 1)
            else:
                # assez proche de la destination en x : déplacement en y
                if pawn.x <= border_x:
                    pawn.move(pawn.y - 1, pawn.x)
                else:  # déplace en x
                    pawn.move(pawn.y, pawn.x - 1)
            break


def build_castle(player: Player):
    """
    Construit des châteaux.

    Au début, cette fonction controle d'un péon
    pour construire le premier château au bon endroit.
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
    if not len(player.castles):
        move_peon_to_first_location(
            player, border, border_y, border_x)

    # Si il y a suffisemment de châteaux ou pas assez d'argent, n'essaie rien
    if len(player.castles) >= min(len_y, len_x) // 2 or player.gold < consts.PRICES[consts.CASTLE]:
        return

    # construit un château au premier moment où un pion est suffisemment loin des châteaux existants
    for pawn in player.pawns:
        if pawn.used:
            continue
        y, x = pawn.coord
        # distance au château le plus proche
        d = cl.distance_to_list((y, x), player.castles)

        # si le pions est suffisamment loin de la bordure
        if border <= x <= border_x and border <= y <= border_y and d >= 3 and not cl.exists_close(pawn, player.eknights, 2):

            pawn.build()
            return


def create_units(player: Player):
    """Création des unités par le château."""
    n = len(player.eknights) - len(player.defense) - len(player.attack)
    nb_pawn = len(player.pawns)

    for castle in player.castles:
        y, x = castle.coord
        # Nous somme attaqués, production de défenseurs
        # if build_order:
        #     build_order.pop()
        # if player.gold > consts.PRICES[suivant]:
        #     connection.build(suivant, y, x, player.id, player.token)
        #     player.gold -= consts.PRICES[suivant]
        # else:
        #     build_order.append(suivant)
        # else:
        if n > 0:
            if player.gold > consts.PRICES[connection.KNIGHT]:
                connection.build(connection.KNIGHT, y, x,
                                 player.id, player.token)
                player.gold -= consts.PRICES[connection.KNIGHT]
                player.defense.append(Knight(y, x, player))
                n -= 1
        # garder un équilibre entre defense et attaque et produire plus tôt
        elif player.gold > consts.PRICES[connection.KNIGHT] and (2 * len(player.eknights) <= len(player.defense) or len(player._knights) <= 2 / 3 * nb_pawn):
            if connection.build(connection.KNIGHT, y, x, player.id, player.token):
                player.gold -= consts.PRICES[connection.KNIGHT]
                player.attack.append(Knight(y, x, player))
        # trop d'argent on achète des défenseurs
        elif player.gold > consts.PRICES[connection.KNIGHT] * 2 and len(player.castles) >= 2 and nb_pawn > 3:
            if connection.build(connection.KNIGHT, y, x, player.id, player.token):
                player.gold -= consts.PRICES[connection.KNIGHT]
                player.defense.append(Knight(y, x, player))
        # Pas assez d'argent, et de l'argent est disponible sur la carte (ou du brouillard de guerre)
        elif player.gold > consts.PRICES[connection.PAWN] * 1.25 \
                and len(player.good_gold) + len(player.bad_gold) + len(player.fog) > nb_pawn\
                and len(player._knights) >= 2 / 3 * nb_pawn:
            connection.build(connection.PAWN, y, x,
                             player.id, player.token)
            player.gold -= consts.PRICES[connection.PAWN]
            player.pawns.append(Pawn(y, x, player))
