"""Fonctions pour définir les actions d'un attaquant."""

import random as rd
from apis import connection
from apis.connection import Coord
from apis.kinds import Pawn, Knight, Castle, Enemy
import player.logic.client_logic as cl


def prediction_combat(a: int, d: int):
    """
    Prédit le gaganant d'un combat.

    Parameters:
        a (int): Force de l'attaquant.
        d (int): Force du defenseur.

    Returns: tuple (bool, int, int) où:
        - bool: True si l'attaquant gagne, False sinon.
        - int: nombre de pertes de l'attaquant.
        - int: nombre de pertes du défenseur.
    """
    pertes_a = 0
    pertes_d = 0
    while a > 0 and d > 0:
        pertes_a += min(a, (d + 1) // 2)
        a = a - (d + 1) // 2
        pertes_d += min(d, (a + 1) // 2)
        d = d - (a + 1) // 2
    return (d <= 0, pertes_a <= pertes_d, pertes_a, pertes_d)


def compte_soldats_ennemis_cases_adjacentes(player: str, case: tuple[int, int]):
    """Compte les soldats ennemis à une distance de 1 d'une case."""
    y, x = case
    carte = connection.get_map()
    voisins = connection.get_moves(y, x)
    eknight = 0
    for c in voisins:
        eknight += carte[y + c[0]][x + c[1]][player][connection.EKNIGHT]
    return eknight


def move_everyone(case: Coord, allies_voisins: dict[Coord, list[Knight]]):
    """Bouge tous les attaquants sur la case ciblée."""
    for knights in allies_voisins.values():
        while knights:
            knights[-1].move(case[0], case[1])
            knights.pop()


def prediction_attaque(case_attaquee: tuple[int, int], knights: list[Knight], eknights: list[Knight]):
    """
    Regarde les résultats d'un combat en prenant en compte une contre attaque sur la case au tour suivant.

    Parameters:
        case_attaquee: case que l'on souhaite attaquée, ou il y a les défenseurs ennemis.
        knights: liste de nos attaquants.
        eknights: liste des défenseurs ennemis.

    Returns:
        bool: True si l'attaque est favorable, False sinon.
    """
    if not eknights:
        return True
    allies_voisins, attaquants = cl.neighbors(case_attaquee, knights)
    defenseurs_voisins, defenseurs_voisins_nombre = cl.neighbors(
        case_attaquee, eknights)
    defenseurs = connection.get_map(
    )[case_attaquee[0]][case_attaquee[1]][eknights[0].player][connection.KNIGHT]
    b1, b2, pertes_attaque, pertes_defense = prediction_combat(
        attaquants, defenseurs)
    if b1 and b2:
        attaquants -= pertes_attaque
        b1, b2, pertes_attaque2, pertes_defense2 = prediction_combat(
            attaquants, defenseurs_voisins_nombre)
        return (pertes_attaque + pertes_attaque2) <= (pertes_defense + pertes_defense2)
    else:
        return False


def attaque(case_attaquee: tuple[int, int], knights: list[Knight], eknights: list[Knight]):
    """Si l'attaque sur case_attaquee depuis toutes les cases adjacentes est gagnante alors bouge tous les chevaliers concernés en attaque."""
    allies_voisins = cl.neighbors(case_attaquee, knights)[0]
    allies_voisins_exploitable = allies_voisins[(1, 0)] + allies_voisins[(0, 1)] + allies_voisins[(-1, 0)] + allies_voisins[(0, -1)]
    allies_voisins_exploitable = list(filter(lambda allie: not (allie.used), allies_voisins_exploitable))
    present_eknight = list(filter(lambda ennemy: (ennemy.y, ennemy.x) == case_attaquee, eknights))
    if prediction_attaque(case_attaquee, allies_voisins_exploitable, present_eknight):
        move_everyone(case_attaquee, allies_voisins_exploitable)


def hunt(knights: list[Knight], epawns: list[Pawn], eknights: list[Knight]):
    """Chasse les péons adverses, en assignant un chevalier à un péon adverse qui va le traquer."""
    for k in knights:
        if k.used:
            continue
        voisins, nb_allies = cl.neighbors(k.coord, epawns)
        voisins_ennemis, _ = cl.neighbors(k.coord, eknights)
        # if somme:
        #     for coord, neighbor in voisins.items():
        #         if neighbor and not voisins_ennemis[]:
        #             k.move(k.y + i[0], k.x + i[1])

    not_used_knights = list(filter(lambda knight: not knight.used, knights))
    if not_used_knights and epawns:
        
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        vus = []
        for k, ep in cl.hongrois_distance(not_used_knights, epawns):
            vus.append(not_used_knights[k])
            y, x = not_used_knights[k].coord
            i, j = epawns[ep].coord
            if abs(y - i) + abs(x - j) == 1:
                attaque((i, j), not_used_knights, eknights)
            else:
                if rd.random() > 0.5:  # pour ne pas que le chevalier aille toujours d'abord en haut puis à gauche
                    if x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        not_used_knights[k].move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        not_used_knights[k].move(y, x + 1)
                    elif y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        not_used_knights[k].move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        not_used_knights[k].move(y + 1, x)
                else:
                    if y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        not_used_knights[k].move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        not_used_knights[k].move(y + 1, x)
                    elif x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        not_used_knights[k].move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        not_used_knights[k].move(y, x + 1)


def destroy_castle(knights: list[Knight], castles: list[Castle],
                   eknights: list[Knight]):
    """Chasse les chateaux adverses, si possibilité de le détruire, le détruit."""
    knights_not_used = list(filter(lambda knight: not knight.used, knights))
    if knights_not_used and castles:
        # probleme d'affectation
        # choisis les chateaux vers lesquelles vont se diriger les chevaliers
        # pour en minimiser le nombre total de mouvements
        vus = []
        for k, ep in cl.hongrois_distance(knights_not_used, castles):
            vus.append(knights_not_used[k])
            y, x = knights_not_used[k].coord
            i, j = castles[ep].coord
            if abs(y - i) + abs(x - j) == 1:
                attaque((i, j), knights_not_used, eknights)
            else:
                if rd.random() > 0.5:  # pour ne pas que le chevalier aille toujours d'abord en haut puis à gauche
                    if x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        knights_not_used[k].move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        knights_not_used[k].move(y, x + 1)
                    elif y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        knights_not_used[k].move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        knights_not_used[k].move(y + 1, x)
                else:
                    if y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        knights_not_used[k].move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        knights_not_used[k].move(y + 1, x)
                    elif x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        knights_not_used[k].move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        knights_not_used[k].move(y, x + 1)

def free_pawn(knights: list[Knight], eknights: list[Knight], epawns: list[Enemy]):
    """Attaque les péons gratuits s'ils sont adjacent à un chevalier libre."""
    for knight in knights:
        if not knight.used:
            for epawn in epawns:
                if cl.distance(knight.x, knight.y, epawn.x, epawn.y) == 1 and epawn not in eknights:
                    knight.move(epawn.y, epawn.x)

# def endgame(knights: list[Knight], eknights: list[Knight], epawns: list[Pawn]):
#     knights_not_used = list(filter(lambda knight: not knight.used, knights))
#     if eknights:
#         while knights_not_used:
#             vus=[]
#             for k, ep in cl.hongrois_distance(knights_not_used, castles):
#                 vus.append(knights_not_used[k])
#                 y, x = knights_not_used[k].coord
#                 i, j = eknights[ep].coord
#                 if abs(y - i) + abs(x - j) == 1:
#                     attaque((i, j), knights_not_used, eknights)
#                 else:
#                     if rd.random() > 0.5:  # pour ne pas que le chevalier aille toujours d'abord en haut puis à gauche
#                         if x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
#                             knights_not_used[k].move(y, x - 1)
#                         elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
#                             knights_not_used[k].move(y, x + 1)
#                         elif y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
#                             knights_not_used[k].move(y - 1, x)
#                         elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
#                             knights_not_used[k].move(y + 1, x)
#                     else:
#                         if y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
#                             knights_not_used[k].move(y - 1, x)
#                         elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
#                             knights_not_used[k].move(y + 1, x)
#                         elif x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
#                             knights_not_used[k].move(y, x - 1)
#                         elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
#                             knights_not_used[k].move(y, x + 1)
#             knights_not_used = list(filter(lambda knight: not knight.used, knights))