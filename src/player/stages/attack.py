"""
Fonctions pour définir les actions d'un attaquant
"""

import random as rd
from apis import connection
from apis.connection import Coord
from apis.kinds import Pawn, Knight, Castle
import player.logic.client_logic as cl


def prediction_combat(a: int, d: int):
    """
    Prédit le gaganant d'un combat

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
    """
    compte les soldats ennemis à une distance de 1 d'une case
    """
    y, x = case
    carte = connection.get_map()
    voisins = connection.get_moves(y, x)
    eknight = 0
    for c in voisins:
        eknight += carte[y + c[0]][x + c[1]][player][connection.EKNIGHT]
    return eknight


def move_everyone(case: Coord, allies_voisins: dict[Coord, list[Knight]]):
    """
    Bouge tous les attaquants sur la case ciblée
    """
    for knights in allies_voisins.values():
        while knights:
            knights[-1].move(case[0], case[1])
            knights.pop()


def prediction_attaque(case_attaquee: tuple[int, int], knights: list[Knight], eknights: list[Knight]):
    """
    Regarde les résultats d'un combat en prenant en compte une contre attaque sur la case au tour suivant

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
    """si l'attaque sur case_attaquee est gagnante """
    allies_voisins, _ = cl.neighbors(case_attaquee, knights)[0]
    allies_voisins_exploitable = allies_voisins[(1, 0)] + allies_voisins[(0, 1)] + allies_voisins[(-1, 0)] + allies_voisins[(0, -1)]
    allies_voisins_exploitables = list(filter(lambda allie: score >= 70, scores))
    if prediction_attaque(case_attaquee, allies_voisins_exploitable, eknights):
        move_everyone(case_attaquee, allies_voisins_exploitable)


def hunt(knights: list[Knight], epawns: list[Pawn], eknights: list[Knight]):
    """ 
    chasse les péons adverses, en assignant un chevalier à un péon adverse qui va le traquer
    """
    for k in knights:
        voisins, nb_allies = cl.neighbors(k.coord, epawns)
        voisins_ennemis, _ = cl.neighbors(k.coord, eknights)
        # if somme:
        #     for coord, neighbor in voisins.items():
        #         if neighbor and not voisins_ennemis[]:
        #             k.move(k.y + i[0], k.x + i[1])

    if knights and epawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        vus = []
        for k, ep in cl.hongrois_distance(knights, epawns):
            vus.append(knights[k])
            y, x = knights[k].coordinate()
            i, j = epawns[ep].coordinate()
            if abs(y - i) + abs(x - j) == 1:
                attaque((i, j), knights, eknights)
            else:
                if rd.random() > 0.5:  # pour ne pas que le chevalier aille toujours d'abord en haut puis à gauche
                    if x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        k.move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        k.move(y, x + 1)
                    elif y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        k.move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        k.move(y + 1, x)
                else:
                    if y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        k.move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        k.move(y + 1, x)
                    elif x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        k.move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        k.move(y, x + 1)


def destroy_castle(knights: list[Knight], castles: list[Castle],
                   eknights: list[Knight]):
    """
    chasse les chateaux adverses, si possibilité de le détruire, le détruit
    """
    if knights and castles:
        # probleme d'affectation
        # choisis les chateaux vers lesquelles vont se diriger les chevaliers
        # pour en minimiser le nombre total de mouvements
        vus = []
        for k, ep in cl.hongrois_distance(knights, castles):
            vus.append(knights[k])
            y, x = knights[k].coordinate()
            i, j = castles[ep].coordinate()
            if abs(y - i) + abs(x - j) == 1:
                attaque((i, j), knights, eknights)
            else:
                if rd.random() > 0.5:  # pour ne pas que le chevalier aille toujours d'abord en haut puis à gauche
                    if x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        k.move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        k.move(y, x + 1)
                    elif y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        k.move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        k.move(y + 1, x)
                else:
                    if y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == []:
                        k.move(y - 1, x)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == []:
                        k.move(y + 1, x)
                    elif x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == []:
                        k.move(y, x - 1)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == []:
                        k.move(y, x + 1)
        for k in vus:  # j'enlève ceux que je bouge
            knights.remove(k)


def free_pawn(knights: list[Knight], eknights: list[Knight], epawns: list[Pawn]):
    """
        libère les péons bloqués par les chevaliers adverses
        """
    for knight in knights:
        if not knight.used:
            for epawn in epawns:
                if cl.distance(knight.x, knight.y, epawn.x, epawn.y) == 1 and epawn not in eknights:
                    knight.move(epawn[0], epawn[1])
