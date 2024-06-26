"""Gestion des château : construction et production."""


from __future__ import annotations
from typing import TYPE_CHECKING

from apis import connection
from config import consts, settings
import logic.client_logic as cl
from apis.kinds import Castle, Coord

if TYPE_CHECKING:
    from apis.players.players import Player

build_order = []


def move_peon_to_first_location(player: Player, border: int, border_y: int, border_x: int):
    """Construit le premier château."""
    destination = (border, border) if player == "A" else (border_y, border_x)
    d = cl.distance_to_list(destination, player.pawns)[0]
    # si d == 0, le pion est au bon endroit
    # donc il va construire un château ici
    if not d:
        global move_to_first_castle
        move_to_first_castle = False
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


move_to_first_castle = True
first_castle_built = False


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
    if not len(player.castles) and move_to_first_castle:
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
                    global first_castle_built
                    if not first_castle_built:
                        global build_order
                        build_order = ['attack'] + (len(player.good_gold) + 1) * ['pawn']
                        print('build_order: ', build_order)
                    pawn.build()
                    first_castle_built = True
                    return


def get_nb_castles():
    """Renvoie le nombre de châteaux que l'on devra construire."""
    len_y, len_x = connection.size_map()
    return min(len_y, len_x) // settings.CASTLES_RATIO


def nb_units_near_castles(castle: Castle, coords: list[Coord], radius: int):
    """Renvoie le nombre d'unités dans un rayon donné autour d'un château."""
    return len([0 for unit in coords if cl.distance(*unit.coord, *castle.coord) <= radius])


def create_units(player: Player):
    """Création des unités par le château."""
    if not build_order:
        eknight_offset = len(player.eknights) - len(player.defense)
        len_golds = len(player._golds)
        missing_priority_castles = len(player.castles) < get_nb_castles() // settings.PRIORITISED_CASTLES_RATIO
        for castle in player.castles:
            # 1. Nous sommes attaqués, production de défenseurs
            if (nb_units_near_castles(castle, player.eknights, 6) > 1.5 * nb_units_near_castles(castle, player.defense, 6)
                    or nb_units_near_castles(castle, player.eknights, 2) > nb_units_near_castles(castle, player.defense, 0)):
                print("---priory1---")
                if player.gold >= consts.PRICES[consts.KNIGHT]:
                    castle.create_defense()
                    eknight_offset -= 1
                break
            # 2. Vraiment pas assez de péon
            elif nb_units_near_castles(castle, player.good_gold, settings.DISTANCE_BETWEEN_CASTLES) >= len(player.pawns):
                print("---priory2---")
                if player.gold >= consts.PRICES[consts.PAWN]:
                    castle.create_pawn()
            # 3. Il y a des péons ennemis
            elif len(player.epawns) >= settings.PAWNS_KNIGHTS_RATIO * len(player.attack):
                print("---priory3---")
                if player.gold >= consts.PRICES[consts.KNIGHT] + consts.PRICES[consts.KNIGHT]:
                    castle.create_attack()
            # 4. Pas assez de péons
            elif len_golds > 1.5 * len(player.pawns):
                print("---priory4---")
                if player.gold >= consts.PRICES[consts.PAWN] + consts.PRICES[consts.KNIGHT]:
                    castle.create_pawn()
            # 5. Production d'attaquants
            elif player.gold >= consts.PRICES[consts.KNIGHT] + consts.PRICES[consts.KNIGHT]:
                print("---priory5---")
                castle.create_attack()
    else:
        for castle in player.castles:
            if build_order[-1] == 'pawn':
                if player.gold >= consts.PRICES[consts.PAWN]:
                    castle.create_pawn()
                    build_order.pop()
            elif build_order[-1] == 'attack':
                if player.gold >= consts.PRICES[consts.KNIGHT]:
                    castle.create_attack()
                    build_order.pop()
