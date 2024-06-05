"""Module pour jouer des péons."""

from __future__ import annotations
from typing import TYPE_CHECKING

import random as rd
from apis import connection
from apis.kinds import Pawn, Knight, Unit, GoldPile
import player.logic.client_logic as cl
import player.stages.exploration as ex

if TYPE_CHECKING:
    from apis.players import Player


def fuite(pawns: list[Pawn], knights: list[Knight], eknights: list[Knight], defense: list[Knight]):
    """Les péons fuient les chevaliers ennemis s'ils sont en danger."""
    i = 0
    knights_not_used = [k for k in knights if not k.used]
    while i < len(pawns):
        p = pawns[i]
        i += 1
        direc_enemies, total_enemies = cl.neighbors((p.y,p.x), eknights)
        if total_enemies > 0:
            direc_allies, allies_backup = cl.neighbors((p.y,p.x), knights_not_used)
            allies = 0
            allies_defense = 0
            on_case = []
            for k in knights_not_used:
                if k.used:
                    continue
                if k.y == p.y and k.x == p.x:
                    on_case.append(k)
                    allies += 1
            for k in defense:
                if k.used:
                    continue
                if k.y == p.y and k.x == p.x:
                    on_case.append(k)
                    allies += 1

            if cl.prediction_combat(total_enemies, allies + allies_backup)[0]:
                # si on perd le combat même avec les alliés on fuit
                for (direc, nb) in direc_enemies.items():
                    if nb == 0 and (p.y + direc[0], p.x + direc[1]) in connection.get_moves(p.y, p.x) and\
                            cl.neighbors((p.y + direc[0], p.x + direc[1]), eknights)[1] == 0:
                        p.move(p.y + direc[0], p.x + direc[1])
                        i -= 1
                        break
            else:
                while cl.prediction_combat(total_enemies, allies_defense)[0] and len(on_case) > 0:
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
    """Récolte l'or quand c'est possible, sinon ce déplace vers la pile disponible la plus proche."""
    pawns = [unit for unit in player.pawns if not unit.used]
    eknights = player.eknights
    ecastles = player.ecastles

    # print("BEFORE PAWNS", pawns)

    # simple_gold = golds
    if golds and pawns:

        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        # je fais bouger les peons vers leur mine d'or
        result_data = cl.hongrois_distance(pawns, golds) ####
        for p, g in result_data:
            gold = golds[g]
            y, x = pawns[p].coord
            i, j = gold.y, gold.x
            if rd.random() > 0.5:  # pour ne pas que le peon aille toujours d'abord en haut puis à gauche
                if x > j and (y, x - 1) not in eknights and (y, x - 1) not in ecastles and \
                        (cl.neighbors((y, x - 1), eknights)[1] == 0 or cl.neighbors((y, x - 1), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y, x - 1)
                elif x < j and (y, x + 1) not in eknights and (y, x + 1) not in ecastles and \
                        (cl.neighbors((y, x + 1), eknights)[1] == 0 or cl.neighbors((y, x + 1), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y, x + 1)
                elif y > i and (y - 1, x) not in eknights and (y - 1, x) not in ecastles and \
                        (cl.neighbors((y - 1, x), eknights)[1] == 0 or cl.neighbors((y - 1, x), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y - 1, x)
                elif y < i and (y + 1, x) not in eknights and (y + 1, x) not in ecastles and \
                        (cl.neighbors((y + 1, x), eknights)[1] == 0 or cl.neighbors((y + 1, x), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y + 1, x)
                else:
                    pawns[p].farm(gold)
            else:
                if y > i and (y - 1, x) not in eknights and (y - 1, x) not in ecastles and \
                        (cl.neighbors((y - 1, x), eknights)[1] == 0 or cl.neighbors((y - 1, x), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y - 1, x)
                elif y < i and (y + 1, x) not in eknights and (y + 1, x) not in ecastles and \
                        (cl.neighbors((y + 1, x), eknights)[1] == 0 or cl.neighbors((y + 1, x), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y + 1, x)
                elif x > j and (y, x - 1) not in eknights and (y, x - 1) not in ecastles and \
                        (cl.neighbors((y, x - 1), eknights)[1] == 0 or cl.neighbors((y, x - 1), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y, x - 1)
                elif x < j and (y, x + 1) not in eknights and (y, x + 1) not in ecastles and \
                        (cl.neighbors((y, x + 1), eknights)[1] == 0 or cl.neighbors((y, x + 1), eknights)[1] <= len(connection.get_eknights(y, x))):
                    pawns[p].move(y, x + 1)
                else:
                    pawns[p].farm(gold)
    # print("AFTER PAWNS", pawns)


def path(units: list[Unit], other_units: list[Unit], eknights: list[Knight]):
    """
    Trouve un chemin utile en un mouvement pour les péons.

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
            units_to_move = [unit for unit in units_to_move if unit is not bestpawn]
        else:
            break
    for choice in results:
        choice[0].move(choice[1][0], choice[1][1])


def explore(player: Player, otherunits=[]):
    """Envoie en exploration les "pawns" inactifs pour le tour."""


    eknights = player.eknights

    path(player.pawns, otherunits, eknights)
    farm(player, player.bad_gold)
    ex.path_trou(player.pawns, otherunits, eknights)


def explore_knight(player: Player, otherunits=[]):
    """Envoie en exploration les chevaliers inactifs pour le tour."""
    eknights = player.eknights

    path(player.eknights, otherunits, eknights)
    ex.path_trou(player.eknights, otherunits, eknights)
