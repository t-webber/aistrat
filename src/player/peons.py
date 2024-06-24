"""Module pour jouer des péons."""

from __future__ import annotations
from typing import TYPE_CHECKING

from apis.kinds import Pawn, Knight, Unit, GoldPile
import logic.client_logic as cl
import player.exploration as ex

if TYPE_CHECKING:
    from apis.players.players import Player


def fuite(pawns: list[Pawn], knights: list[Knight], eknights: list[Knight]):
    """Les péons fuient les chevaliers ennemis s'ils sont en danger."""
    i = 0
    knights_not_used = [k for k in knights if not k.used]
    while i < len(pawns):
        p = pawns[i]
        i += 1
        _, total_enemies = cl.neighbors((p.y, p.x), eknights)
        if total_enemies > 0:
            direc_allies, allies_backup = cl.movable_neighbors((p.y, p.x), knights_not_used)
            allies = 0
            allies_defense = 0
            on_case = []
            for k in knights_not_used:
                if k.used:
                    continue
                if k.y == p.y and k.x == p.x:
                    on_case.append(k)
                    allies += 1

            if cl.prediction_combat(total_enemies, allies + allies_backup)[0]:
                # si on perd le combat même avec les alliés on fuit
                if cl.move_safe_random_without_purpose(p, eknights, knights):
                    continue
            else:
                while cl.prediction_combat(total_enemies, allies_defense)[0] and len(on_case) > 0:
                    on_case[-1].used = True
                    allies_defense += 1
                # on peut réussir à gagner le combat avec les alliés et on le fait venir
                while cl.prediction_combat(total_enemies, allies)[0] and allies_backup > 0:
                    for _, list_allies in direc_allies.items():
                        if list_allies:
                            list_allies[-1].move(p.y, p.x)
                            knights_not_used.remove(list_allies[-1])
                            list_allies.pop()
                            allies_backup -= 1
                            allies += 1
                            break


def farm(player: Player, golds: list[GoldPile]):
    """Récolte l'or quand c'est possible, sinon ce déplace vers la pile disponible la plus proche."""
    pawns = [unit for unit in player.pawns if not unit.used]
    eknights = player.eknights
    ecastles = player.ecastles

    # simple_gold = golds
    if golds and pawns:

        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        # je fais bouger les peons vers leur mine d'or
        result_data = cl.hongrois_distance(pawns, golds)
        for p, g in result_data:
            gold = golds[g]
            y, x = pawns[p].coord
            i, j = gold.y, gold.x
            if y == i and x == j:
                pawns[p].farm(gold)
            else:
                cl.move_safe_random(pawns[p], eknights, ecastles, i, j)


def path(units: list[Unit], other_units: list[Unit], eknights: list[Knight]):
    """
    Trouve un chemin utile en un mouvement pour les péons.

    Essaye de chercher un chemin d'exploration optimal pour les units_to_move pour révéler
    le maximum de la carte pour les péons. Prend en compte other_units pour la visibilité
    """
    units_to_move = [unit for unit in units if not unit.used]
    strategie = 0
    for i in range(len(units_to_move)):
        if strategie == 0:
            bestpawn, bestmove = ex.path_one(
                units_to_move, other_units, eknights)
            if bestpawn == (-1, -1):
                strategie = 1
                i -= 1
                continue
            if bestmove == (bestpawn.y, bestpawn.x):
                return # on n'a pas interet les bouger pour les peons restants
            else:
                bestpawn.move(bestmove[0], bestmove[1])
            #results.append((bestpawn, bestmove))
            other_units.append(bestpawn)
            units_to_move.remove(bestpawn)
        else:
            break


def explore(player: Player, otherunits=[]):
    """Envoie en exploration les "pawns" inactifs pour le tour."""
    eknights = player.eknights
    path(player.pawns, otherunits, eknights)
    farm(player, player.bad_gold)
    ex.path_trou(player.pawns, otherunits, eknights)


def explore_knight(player: Player, otherunits=[]):
    """Envoie en exploration les chevaliers inactifs pour le tour."""
    eknights = player.eknights
    knights = player.attack + player.defense
    path(knights, otherunits, eknights)
    ex.path_trou(knights, otherunits, eknights)
