"""Gestion des château : construction et production."""


from __future__ import annotations
from typing import TYPE_CHECKING

from apis import connection
from config import consts, settings
import logic.client_logic as cl
from apis.kinds import Unit, Castle

if TYPE_CHECKING:
    from apis.players.players import Player


def move_peon_to_first_location(player: Player, border: int, border_y: int, border_x: int):
    """Construit le premier château."""
    destination = (border, border) if player == "A" else (border_y, border_x)
    d = cl.distance_to_list(destination, player.pawns)[0]
    # si d == 0, le pion est au bon endroit
    # donc il va construire un château ici
    if not d:
        global HARD_CODE
        HARD_CODE = False
        return

    for pawn in player.pawns:
        if pawn.used:
            continue
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


HARD_CODE = True


def build_castle(player: Player):
    """
    Construit des châteaux.

    Au début, cette fonction controle d'un péon
    pour construire le premier château au bon endroit.
    """
    len_y, len_x = connection.size_map()

    # Définis les bordures pour ne pas y construire de château
    border = 2
    border_y = len_y - 1 - border
    border_x = len_x - 1 - border

    # Si aucun château n'a été construit, prend le controle d'un pion,
    # le met en (2,2) pour construire un château
    if not len(player.castles) and HARD_CODE:
        move_peon_to_first_location(player, border, border_y, border_x)

    # Si il y a suffisemment de châteaux ou pas assez d'argent, on ne peut pas construire
    if len(player.castles) >= get_nb_castles() or player.gold < consts.PRICES[consts.CASTLE]:
        return

    # construit un château au premier moment où un pion est suffisemment loin des châteaux existants
    for pawn in player.pawns:
        if pawn.used:
            continue
        y, x = pawn.coord
        # suffisamment loin de la bordure
        if border <= x <= border_x and border <= y <= border_y:
            # suffisamment loin des autres châteaux
            if cl.distance_to_list((y, x), player.castles)[0] >= settings.DISTANCE_BETWEEN_CASTLES:
                # suffisamment loin des autres péons
                if not cl.exists_close(pawn, player.eknights, 2):
                    pawn.build()
                    return


def get_nb_castles():
    """Renvoie le nombre de châteaux que l'on devra construire."""
    len_y, len_x = connection.size_map()
    return min(len_y, len_x) // settings.CASTLES_RATIO


def nb_units_near_castles(castle: Castle, units: list[Unit], radius: int):
    """Renvoie le nombre d'unités dans un rayon donné autour d'un château."""
    return len([0 for unit in units if cl.distance(*unit.coord, *castle.coord) <= radius])


def create_units(player: Player):
    """Le château céé des unitées."""
    n = len(player.eknights) - len(player._knights)
    nb_pawn = len(player.pawns)
    for castle in player.castles:
        y, x = castle.coord
        # Nous somme attaqués, production de défenseurs
        if n > 0:
            if player.gold > consts.PRICES[consts.KNIGHT]:
                castle.create_defense()
                n -= 1
        # garder un équilibre entre defense et attaque et produire plus tôt
        elif player.gold > consts.PRICES[consts.KNIGHT] and (2 * len(player.attack) <= len(player.defense) or len(player.attack) <= 2 / 3 * nb_pawn):
            castle.create_attack()
        # trop d'argent on achète des défenseurs
        elif player.gold > consts.PRICES[consts.KNIGHT] * 2 and len(player.castles) >= 2 and nb_pawn > 3:
            castle.create_defense()
        # Pas assez d'argent, et de l'argent est disponible sur la carte (ou du brouillard de guerre)
        elif player.gold > consts.PRICES[consts.PAWN] * 1.25 and len(player._golds) + len(player.fog) > nb_pawn and len(player.attack) >= 2 / 3 * nb_pawn:
            castle.create_pawn()
            nb_pawn += 1
