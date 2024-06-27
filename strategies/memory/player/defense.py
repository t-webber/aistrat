"""Fonction pour la gestion de la defense."""
from __future__ import annotations
from typing import TYPE_CHECKING

import random as rd
import logic.client_logic as cl
from apis.kinds import Pawn, Knight, Castle

if TYPE_CHECKING:
    from apis.players.players import Player


def agressiv_defense(defense: list[Knight], epawns: list[Pawn], eknigths: list[Knight], ecastles: list[Castle]):
    """Effectue des attaque d'opportunité avec la défense.

    Regarde les défenseurs déjà sur place et attaque les ennemis proches en
    priorisant les péons ennemis tout en s'assurant que les péons défendus
    le seront toujours pour le reste du tour

    Returns
        None
    """
    for d in defense:
        if d.used:
            continue
        dir_knights, near_eknights = cl.neighbors((d.y, d.x), eknigths)
        dir_pawns, near_epawns = cl.neighbors((d.y, d.x), epawns)
        dir_castles, near_ecastles = cl.neighbors((d.y, d.x), ecastles)

        agressiv_defenders = []
        for d2 in defense:
            if d2.used or d.used:
                continue
            if (d2.y, d2.x) == (d.y, d.x):
                agressiv_defenders.append(d2)
        options = [(len(dir_castles[d]), d) for d in dir_castles if len(dir_castles[d])] \
            + [(len(dir_pawns[d]), d) for d in dir_pawns if len(dir_pawns[d])] \
            + [(len(dir_knights[d]), d) for d in dir_knights if len(dir_knights[d])]
        options.sort()
        for op in options:
            _, direction = op

            will_attack = []

            for i in agressiv_defenders:
                if not i.used:
                    will_attack.append(i)
                if cl.prediction_combat(len(will_attack), len(dir_knights[direction]))[0] :
                    (y2, x2) = (d.y + direction[0], d.x + direction[1])
                    for d in will_attack:
                        d.move(y2, x2)
                    near_eknights -= len(dir_knights[direction])
                    break


def move_defense(defense: list[Knight], pawns: list[Pawn], eknight: list[Knight]):
    """
    Attribue les chevaliers disponibles aux péons donnés et les bouge vers ces péons.

    Returns:
       chevalier de la défense non attribués
    """
    if pawns == []:
        return defense, []
    hongroise = cl.hongrois_distance(defense, pawns)
    for d, p in hongroise:
        yp, xp = pawns[p].coord
        cl.move_safe_random(defense[d], eknight, [], yp, xp)


def defend(pawns: list[Pawn], defense: list[Knight], eknights: list[Knight], castle: list[Castle]):
    """
    Défend les péons en utilisant la strategie de défense.

    attribution par Méthode hongroise priorisé en fonction de
    la distance au ennemis

    Returns:
        None
    """
    needing_help = {}
    # needing_help = [[] for _ in range(50)]

    # ATTENTION les cases avec plusieurs unités seront protégés proportionnelement à leur nombre.
    # Il faudra potentiellement modifier la ponderation/ importance des cases
    units = pawns + castle
    for unit in units:
        for eknight in eknights:
            (y1, x1), (y2, x2) = unit.coord, eknight.coord
            d = cl.distance(x1, y1, x2, y2)
            if d in needing_help:
                needing_help[d].append(unit)
            else:
                needing_help[d] = [unit]

    # on priorise les pions selon la distance à un chevalier ennemi
    # compteur = 0
    for compteur in sorted(needing_help.keys()):
        defense_not_used = [d for d in defense if not d.used]
        if not defense_not_used:
            break
        rd.shuffle(needing_help[compteur])
        move_defense(defense_not_used, needing_help[compteur], eknights)


def eknight_based_defense(defense: list[Knight], eknights: list[Knight], player: Player):
    """Fonction en WIP."""
    defense_id = []
    eknight_id = []
    attributions = dict([(eknights[i], (-1, None))
                        for i in range(len(eknight_id))])
    for defender in defense_id:
        min = 1000000000
        cible = None
        for attacker in eknight_id:
            dist = abs(attacker[0][0] - defender[0][0]) * 5 - \
                (abs(attacker[0][0] - defender[0][0]) == 1) * 4
            if player == 'A':
                dist += abs(attacker[0][1] - defender[0][1]) * (
                    ((attacker[0][1] - defender[0][1]) > 0) + 5 * ((attacker[0][1] - defender[0][1]) < 0))
            elif player == 'B':
                dist += abs(attacker[0][1] - defender[0][1]) * (
                    5 * ((attacker[0][1] - defender[0][1]) > 0) + ((attacker[0][1] - defender[0][1]) < 0))
            if dist < min and (dist < attributions[attacker][0] or attributions[attacker][0] == -1):
                min = dist
                cible = attacker
        if cible is not None:
            old_defender = attributions[cible][1]
            attributions[cible] = (min, defender)
            if old_defender is not None:
                defense_id.append(old_defender)

    for (attacker, i) in attributions:
        _, defender = attributions[(attacker, i)]
        if defender is not None:
            yd, xd = defender
            if (attacker[0] - defender[0] > 0):
                defender.move(yd - 1, xd)
            elif (attacker[0] - defender[0] < 0):
                defender.move(yd + 1, xd)
            elif (attacker[1] - defender[1] > 1 * (player == 'A')):
                defender.move(yd, xd - 1)
            elif (attacker[1] - defender[1] < (-1) * (player == 'B')):
                defender.move(yd, xd + 1)
    return ()
