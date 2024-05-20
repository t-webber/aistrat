from __future__ import annotations
from typing import TYPE_CHECKING

import random as rd
import player.logic.client_logic as cl
from apis.kinds import Pawn, Knight, Castle

if TYPE_CHECKING:
    from apis.players import Player


def agressiv_defense(defense: list[Knight], epawns: list[Pawn], player: Player,
                     token, eknigths: list[Knight]):
    '''
    Regarde les défenseurs déjà sur place et attaque les ennemis proches en
    priorisant les péons ennemis tout en s'assurant que les péons défendus
    le seront toujours pour le reste du tour

    Returns
        None
    '''
    for d in defense:
        dir_knights, near_eknights = cl.neighbors(d, eknigths)
        dir_pawns, near_epawns = cl.neighbors(d, epawns)

        if near_epawns == [] and near_eknights == []:
            return

        agressiv_defenders = []
        for d2 in defense:
            if (d2.y, d2.x) == (d.y, d.x):
                agressiv_defenders += d2

        options = [(dir_pawns[d], d) for d in dir_knights]
        options.sort()
        for op in options:
            _, direction = op

            will_attack = []

            for i in agressiv_defenders:

                will_attack += i
                if cl.prediction_combat(len(will_attack), dir_knights[direction])[0] and\
                        not (cl.prediction_combat(len(near_eknights)-dir_knights[direction], len(agressiv_defenders)-len(will_attack))[0]):
                    (y, x), (y2, x2) = d, (d[0] +
                                           direction[0], d[1]+direction[1])
                    for to_move in will_attack:
                        defense.remove(to_move)
                        d.move(y2, x2)
                        cl.move_unit(y, x, y2, x2, player)
                    agressiv_defenders -= i
                    near_eknights -= dir_knights[direction]


def move_defense(defense: list[Knight], pawns: list[Pawn], eknight: list[Knight]):
    """
    attribue les chevaliers disponibles aux péons donnés et les bouge
    vers ces péons

    Returns:
       chevalier de la défense non attribués
    """
    if pawns == []:
        return defense, []
    hongroise = cl.hongrois_distance(defense, pawns)
    utilise = []
    arrived = []
    for d, p in hongroise:
        yd, xd = defense[d].y, defense[d].x
        yp, xp = pawns[p].y, pawns[p].x
        utilise.append(defense[d])
        # Pour ne pas que le defenseur aille toujours
        # d'abord en haut puis à gauche
        if rd.random() > 0.5:
            if xd > xp and (cl.find_unit(eknight, yd, xd - 1) is not None):
                defense[d].move(yd, xd-1)
            elif xd < xp and (cl.find_unit(eknight, yd, xd + 1) is not None):
                defense[d].move(yd, xd+1)
            elif yd > yp and (cl.find_unit(eknight, yd - 1, xd) is not None):
                defense[d].move(yd - 1, xd)
            elif yd < yp and (cl.find_unit(eknight, yd + 1, xd) is not None):
                defense[d].move(yd + 1, xd)
            else:
                arrived.append(defense[d])
        else:
            if yd > yp and (cl.find_unit(eknight, yd - 1, xd) is not None):
                defense[d].move(yd-1, xd)
            elif yd < yp and (cl.find_unit(eknight, yd + 1, xd) is not None):
                defense[d].move(yd+1, xd)
            elif xd > xp and (cl.find_unit(eknight, yd, xd - 1) is not None):
                defense[d].move(yd, xd-1)
            elif xd < xp and (cl.find_unit(eknight, yd, xd + 1) is not None):
                defense[d].move(yd, xd+1)
            else:
                arrived.append(defense[d])

    for d in utilise:
        defense.remove(d)
    return (defense, arrived)


def defend(pawns: list[Pawn], defense: list[Knight], eknights: list[Knight], castle: list[Castle], player, token):
    """
    Défend les péons en utilisant la strategie de défense

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
    left_defense = defense.copy()
    arrived = []
    for compteur in sorted(d.keys()):
        if not left_defense:
            break
        rd.shuffle(needing_help[compteur])
        left_defense, arrived2 = move_defense(
            left_defense, needing_help[compteur], eknights)
    arrived += arrived2
    return arrived


def eknight_based_defense(defense: list[Knight], eknights: list[Knight], player: Player):
    defense_id = [(defense[i], i) for i in range(len(defense))]
    eknight_id = [(eknights[i], i) for i in range(len(eknights))]
    attributions = dict([(eknight_id[i], (-1, None))
                        for i in range(len(eknight_id))])
    for defender in defense_id:
        print("oui")
        min = 1000000000
        cible = None
        for attacker in eknight_id:
            dist = abs(attacker[0][0]-defender[0][0])*5 - \
                (abs(attacker[0][0]-defender[0][0]) == 1)*4
            if player == 'A':
                dist += abs(attacker[0][1]-defender[0][1])*(
                    ((attacker[0][1]-defender[0][1]) > 0) + 5*((attacker[0][1]-defender[0][1]) < 0))
            elif player == 'B':
                dist += abs(attacker[0][1]-defender[0][1])*(
                    5*((attacker[0][1]-defender[0][1]) > 0) + ((attacker[0][1]-defender[0][1]) < 0))
            if dist < min and (dist < attributions[attacker][0] or attributions[attacker][0] == -1):
                min = dist
                cible = attacker
                print("attrib")
        if cible is not None:
            print("attrib def")
            old_defender = attributions[cible][1]
            attributions[cible] = (min, defender)
            if old_defender is not None:
                defense_id.append(old_defender)

    for (attacker, i) in attributions:
        _, defender = attributions[(attacker, i)]
        if defender is not None:
            yd, xd = defender
            if (attacker[0]-defender[0] > 0):
                defender.move(yd-1, xd)
            elif (attacker[0]-defender[0] < 0):
                defender.move(yd+1, xd)
            elif (attacker[1]-defender[1] > 1*(player == 'A')):
                defender.move(yd, xd-1)
            elif (attacker[1]-defender[1] < (-1)*(player == 'B')):
                defender.move(yd, xd+1)
    return ()
