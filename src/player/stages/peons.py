from __future__ import annotations
from typing import TYPE_CHECKING

import random as rd
from typing import Set
from apis import connection
from apis.kinds import Pawn, Knight, Castle, Unit, GoldPile
import player.logic.client_logic as cl
import player.stages.exploration as ex

if TYPE_CHECKING:
    from apis.players import Player


def fuite(pawns: Set[Pawn], knights: Set[Knight], eknights: Set[Knight], defense: Set[Knight]):
    i = 0
    while i < len(pawns):
        p = pawns[i]
        i += 1
        direc_enemies, total_enemies = cl.neighbors(p, eknights)
        if total_enemies > 0:
            direc_allies, allies_backup = cl.neighbors(p, knights)
            allies = 0
            allies_defense = 0
            on_case = []
            for k in knights:
                if k.y == p.y and k.x == p.x:
                    on_case.append(k)
                    allies += 1
            for k in defense:
                if k.y == p.y and k.x == p.x:
                    on_case.append(k)
                    allies += 1

            if cl.prediction_combat(total_enemies, allies+allies_backup)[0]:
                # si on perd le combat même avec les alliés on fuit
                for (direc, nb) in direc_enemies.items():
                    if nb == 0 and (p.y + direc[0], p.x+direc[1]) in connection.get_moves(p.y, p.x) and\
                          cl.neighbors((p.y + direc[0], p.x+direc[1]), eknights)[1] == 0:
                        p.move(p.y + direc[0], p.x+direc[1])
                        i -= 1
                        break
            else:
                while cl.prediction_combat(total_enemies, allies_defense)[0] and len(on_case) > 0:
                    on_case[-1].move(on_case[0].y + 1, on_case[0].x)
                    on_case.pop()
                    allies_defense += 1
                # on peut réussir à gagner le combat avec les alliés et on le fait venir
                while cl.prediction_combat(total_enemies, allies)[0] and allies_backup > 0:
                    for direc, list_allies in direc_allies.items():
                        if list_allies:
                            list_allies[-1].move(p.y, p.x)
                            list_allies.pop()
                            allies_backup -= 1
                            allies += 1
                            break


def farm(player: Player, golds: list[GoldPile]):
    """
    récolte l'or quand c'est possible, sinon ce déplace vers la pile disponible la plus proche
    """
    pawns =  [unit for unit in player.pawns if not unit.used]
    eknights = player.eknights
    ecastles = player.ecastles

    # simple_gold = golds
    if golds and pawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        gold_location = []
        gold_location = [(item[0], item[1]) for item in golds]
        # je fais bouger les peons vers leur mine d'or
        result_data = cl.hongrois_distance(pawns, gold_location)
        for p, g in result_data:
            y, x = pawns[p].coord
            i, j, _ = golds[g]
            gold_location.remove((i, j))
            if rd.random() > 0.5:  # pour ne pas que le peon aille toujours d'abord en haut puis à gauche
                if x > j and (y, x - 1) not in eknights and (y, x - 1) not in ecastles and \
                        (cl.neighbors((y, x - 1), eknights)[1] == 0 or cl.neighbors((y, x - 1), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y, x-1)
                elif x < j and (y, x + 1) not in eknights and (y, x + 1) not in ecastles and \
                        (cl.neighbors((y, x + 1), eknights)[1] == 0 or cl.neighbors((y, x + 1), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y, x+1)
                elif y > i and (y - 1, x) not in eknights and (y - 1, x) not in ecastles and \
                        (cl.neighbors((y - 1, x), eknights)[1] == 0 or cl.neighbors((y-1, x), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y-1, x)
                elif y < i and (y + 1, x) not in eknights and (y + 1, x) not in ecastles and \
                        (cl.neighbors((y + 1, x), eknights)[1] == 0 or cl.neighbors((y+1, x), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y+1, x)
                else:
                    connection.farm(y, x, player.id, player.token)
            else:
                if y > i and (y - 1, x) not in eknights and (y - 1, x) not in ecastles and \
                        (cl.neighbors((y - 1, x), eknights)[1] == 0 or cl.neighbors((y-1, x), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y-1, x)
                elif y < i and (y + 1, x) not in eknights and (y + 1, x) not in ecastles and \
                        (cl.neighbors((y + 1, x), eknights)[1] == 0 or cl.neighbors((y+1, x), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y+1, x)
                elif x > j and (y, x - 1) not in eknights and (y, x - 1) not in ecastles and \
                        (cl.neighbors((y, x - 1), eknights)[1] == 0 or cl.neighbors((y, x - 1), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y, x-1)
                elif x < j and (y, x + 1) not in eknights and (y, x + 1) not in ecastles and \
                        (cl.neighbors((y, x + 1), eknights)[1] == 0 or cl.neighbors((y, x + 1), eknights)[1] <= len(connection.get_defenders(y, x))):
                    pawns[p].move(y, x+1)
                else:
                    connection.farm(y, x, player.id, player.token)


def path(units: list[Unit], other_units: list[Unit], eknights: list[Knight]):
    """
    Essaye de chercher un chemin d'exploration optimal pour les units_to_move pour révéler
    le maximum de la carte pour les péons. Prend en compte other_units pour la visibilité
    """
    units_to_move = [unit for unit in units if not unit.used]

    results = []
    strategie = 0
    for i in range(len(units_to_move)):
        if strategie == 0:
            bestpawn, bestmove = ex.path_one(
                units_to_move, other_units, eknights)
            if bestpawn == (-1, -1):
                strategie = 1
                i -= 1
                continue
            results.append((bestpawn, bestmove))
            other_units.append(bestpawn)
            units_to_move = [units_to_move[i] for i in range(
                len(units_to_move)) if units_to_move[i] is not bestpawn]
        else:
            break
    for choice in range(len(results)):
        units_to_move[choice].move(results[choice])


def explore(player : Player, otherunits=[]):
    """ 
    Envoie en exploration les "pawns" inactifs pour le tour
    """

    eknights = player.eknights

    path(player.pawns, otherunits, eknights)
    farm(player, player.bad_gold)
    ex.path_trou(player.pawns, otherunits, eknights)


def explore_knight(player : Player, otherunits=[]):
    """ 
    Envoie en exploration les chevaliers inactifs pour le tour
    """
    eknights = player.eknights

    path(player.eknights, otherunits, eknights)
    ex.path_trou(player.eknights, otherunits, eknights)
