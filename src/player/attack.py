"""Fonctions pour définir les actions d'un attaquant."""

from apis import connection
from apis.connection import Coord
from apis.kinds import Pawn, Knight, Castle, Enemy
from config import consts
import logic.client_logic as cl


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


def move_everyone(case: Coord, allies_voisins: list[Knight]):
    """Bouge tous les attaquants sur la case ciblée."""
    for knight in allies_voisins:
        knight.move(case[0], case[1])


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
    _, attaquants = cl.movable_neighbors(case_attaquee, knights)
    _, defenseurs_voisins_nombre = cl.neighbors(case_attaquee, eknights)
    try:
        defenseurs = connection.get_map()[case_attaquee[0]][case_attaquee[1]][eknights[0].player][connection.KNIGHT]
    except Exception as e:
        raise ValueError(f'data = {connection.get_map()} with case = {case_attaquee} on eknights = {eknights}') from e

    b1, b2, pertes_attaque, pertes_defense = prediction_combat(attaquants, defenseurs)
    if b1 and b2:
        attaquants -= pertes_attaque
        b1, b2, pertes_attaque2, pertes_defense2 = prediction_combat(attaquants, defenseurs_voisins_nombre)
        return (pertes_attaque + pertes_attaque2) <= (pertes_defense + pertes_defense2)
    else:
        return False


def attaque(case_attaquee: tuple[int, int], knights: list[Knight], eknights: list[Knight]):
    """Si l'attaque sur case_attaquee depuis toutes les cases adjacentes est gagnante alors bouge tous les chevaliers concernés en attaque."""
    allies_voisins = cl.neighbors(case_attaquee, knights)[0]
    allies_voisins_exploitable = allies_voisins[(1, 0)] + allies_voisins[(0, 1)] + allies_voisins[(-1, 0)] + allies_voisins[(0, -1)]
    allies_voisins_exploitable = list(filter(lambda ally: not (ally.used), allies_voisins_exploitable))
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

        # > problème d'affectation <
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        vus = []
        for k, ep in cl.hongrois_distance(not_used_knights, epawns):
            vus.append(not_used_knights[k])
            not_used_knights[k].target = epawns[ep]
            y, x = not_used_knights[k].coord
            not_used_knights[k].target = epawns[ep]
            i, j = epawns[ep].coord
            if abs(y - i) + abs(x - j) == 1:
                attaque((i, j), not_used_knights, eknights)
            else:
                if not not_used_knights[k].used:
                    cl.move_without_suicide(not_used_knights[k], eknights, i, j)


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
                if not knights_not_used[k].used:
                    cl.move_without_suicide(knights_not_used[k], eknights, i, j)


def free_pawn(knights: list[Knight], eknights: list[Knight], epawns: list[Enemy], castles: list[Castle]):
    """Attaque les péons et les chateaux gratuits s'ils sont adjacent à un chevalier libre."""
    for knight in knights:
        if not knight.used:
            for castle in castles:
                if cl.distance(knight.x, knight.y, castle.x, castle.y) == 1 and prediction_attaque((castle.y, castle.x), knights, eknights):
                    a = cl.movable_neighbors(castle.coord, knights)[0]
                    allies_voisins_exploitable = []
                    for e in a:
                        allies_voisins_exploitable += a[e]
                    move_everyone(castle.coord, allies_voisins_exploitable)
        if not knight.used:
            for epawn in epawns:
                if cl.distance(knight.x, knight.y, epawn.x, epawn.y) == 1 and prediction_attaque((epawn.y, epawn.x), knights, eknights):
                    a = cl.movable_neighbors(epawn.coord, knights)[0]
                    allies_voisins_exploitable = []
                    for e in a:
                        allies_voisins_exploitable += a[e]
                    move_everyone(epawn.coord, allies_voisins_exploitable)


def endgame(knights: list[Knight], eknights: list[Knight]):
    knights_not_used = list(filter(lambda knight: not knight.used, knights))
    while knights_not_used and eknights:
        vus = []
        for k, ep in cl.hongrois_distance(knights_not_used, eknights):
            vus.append(knights_not_used[k])
            y, x = knights_not_used[k].coord
            i, j = eknights[ep].coord
            if abs(y - i) + abs(x - j) == 1:
                attaque((i, j), knights_not_used, eknights)
            else:
                cl.move_without_suicide(knights_not_used[k], eknights, i, j)
        knights_not_used = list(filter(lambda knight: not knight.used, knights))


def sync_atk(knights: list[Knight], eknights: list[Knight], epawns: list[Enemy], player):
    not_used_knights = list(filter(lambda knight: not knight.used, knights))
    not_used_knights = list(filter(lambda knight: (knight.target is not None), not_used_knights))
    dicoattaque = {}
    for k in not_used_knights:
        dist = 2
        for ep in epawns:
            dist2 = (abs(ep.x - k.target.x) + abs(ep.y - k.target.y))
            if dist2 <= dist:
                dist = dist2
                k.target = ep
    for k in not_used_knights:
        dicoattaque[k.target] = []
    for k in not_used_knights:
        epawn = k.target
        dicoattaque[epawn] = dicoattaque[epawn] + [k]
    for ep in dicoattaque:
        if ep is not None:
            i, j = ep.coord
            Y1 = 0
            Y2 = 0
            Y3 = 0
            X1 = 0
            X2 = 0
            X3 = 0
            for k2 in dicoattaque[ep]:
                if k2.y == i:
                    Y1 += 1
                elif k2.y - i == 1:
                    Y2 += 1
                elif k2.y - i == -1:
                    Y3 += 1
                if k2.x == j:
                    X1 += 1
                elif k2.x - j == 1:
                    X2 += 1
                elif k2.x - j == 1:
                    X3 += 1
            for k in dicoattaque[ep]:
                print("target = ", k.target)
                connection.get_data(player.id, player.token)
                if k.used:
                    continue
                if (connection.get_map()[k.target.y][k.target.x][player.id][consts.KNIGHT]):
                    k.target = None
                else:
                    y, x = k.coord
                    a = i - y
                    b = j - x
                    y2 = 0
                    x2 = 0
                    l, L = connection.size_map()
                    if a > 0:
                        y2 = 1
                    elif a < 0:
                        y2 = -1
                    else:
                        y2 = 0
                    if b > 0:
                        x2 = 1
                    elif b < 0:
                        x2 = -1
                    else:
                        x2 = 0
                    if abs(b) > abs(a) or (abs(b) == abs(a) and (l - y) >= (L - x)):
                        if Y1:
                            if Y2 or Y3:
                                if y == i:
                                    if not (connection.get_eknights(y, x + x2)):
                                        k.move(y, x + x2)
                                    elif (y + 1 < l) and not (connection.get_eknights(y + 1, x)):
                                        k.move(y + 1, x)
                                        Y2 += 1
                                        Y1 -= 1
                                    elif (y - 1 >= 0) and not (connection.get_eknights(y - 1, x)):
                                        k.move(y - 1, x)
                                        Y3 += 1
                                        Y1 -= 1
                                    else:
                                        k.target = None
                                        Y1 -= 1
                                elif y - i == 1:
                                    if not (connection.get_eknights(y, x + x2)):
                                        k.move(y, x + x2)
                                    elif not (connection.get_eknights(y - 1, x)):
                                        k.move(y - 1, x)
                                        Y1 += 1
                                        Y2 -= 1
                                    else:
                                        k.target = None
                                        Y2 -= 1
                                elif y - i == -1:
                                    if not (connection.get_eknights(y, x + x2)):
                                        k.move(y, x + x2)
                                    elif not (connection.get_eknights(y + 1, x)):
                                        k.move(y + 1, x)
                                        Y1 += 1
                                        Y3 -= 1
                                    else:
                                        k.target = None
                                        Y3 -= 1
                                else:
                                    cl.move_without_suicide(k, eknights, i, j)
                            elif Y1 > 1:
                                if y == i:
                                    if (y + 1 < l) and not (connection.get_eknights(y + 1, x)):
                                        k.move(y + 1, x)
                                        Y2 += 1
                                        Y1 -= 1
                                    elif (y - 1 >= 0) and not (connection.get_eknights(y - 1, x)):
                                        k.move(y - 1, x)
                                        Y3 += 1
                                        Y1 -= 1
                                    elif not (connection.get_eknights(y, x + x2)):
                                        k.move(y, x + x2)
                                    else:
                                        k.target = None
                                        Y1 -= 1
                            else:
                                cl.move_without_suicide(k, eknights, i, j)
                        elif Y2 and Y3 and (abs(b) + abs(a) > 2):
                            if y - i == 1:
                                if not (connection.get_eknights(y, x + x2)):
                                    k.move(y, x + x2)
                                elif not (connection.get_eknights(y - 1, x)):
                                    k.move(y - 1, x)
                                    Y1 += 1
                                    Y2 -= 1
                                else:
                                    k.target = None
                                    Y2 -= 1
                            if y - i == -1:
                                if not (connection.get_eknights(y, x + x2)):
                                    k.move(y, x + x2)
                                elif not (connection.get_eknights(y + 1, x)):
                                    k.move(y + 1, x)
                                    Y1 += 1
                                    Y3 -= 1
                                else:
                                    k.target = None
                                    Y3 -= 1
                        elif Y2 and Y3 and (abs(b) + abs(a) == 2):
                            if (connection.get_map()[k.target.y + y2][k.target.x][player.id][consts.KNIGHT]):
                                k.used = True
                            else:
                                if y - i == 1:
                                    if not (connection.get_eknights(y, x + x2)):
                                        k.move(y, x + x2)
                                    elif not (connection.get_eknights(y - 1, x)):
                                        k.move(y - 1, x)
                                        Y1 += 1
                                        Y2 -= 1
                                    else:
                                        k.target = None
                                        Y2 -= 1
                                if y - i == -1:
                                    if not (connection.get_eknights(y, x + x2)):
                                        k.move(y, x + x2)
                                    elif not (connection.get_eknights(y + 1, x)):
                                        k.move(y + 1, x)
                                        Y1 += 1
                                        Y3 -= 1
                                    else:
                                        k.target = None
                                        Y3 -= 1
                        elif Y2 or Y3:
                            if y - i == 1:
                                if not (connection.get_eknights(y - 1, x)):
                                    k.move(y - 1, x)
                                    Y1 += 1
                                    Y2 -= 1
                                elif not (connection.get_eknights(y, x + x2)):
                                    k.move(y, x + x2)
                                else:
                                    k.target = None
                                    Y2 -= 1
                            if y - i == -1:
                                if not (connection.get_eknights(y + 1, x)):
                                    k.move(y + 1, x)
                                    Y1 += 1
                                    Y3 -= 1
                                elif not (connection.get_eknights(y, x + x2)):
                                    k.move(y, x + x2)
                                else:
                                    k.target = None
                                    Y3 -= 1
                        else:
                            cl.move_without_suicide(k, eknights, i, j)
                    else:
                        if X1:
                            if X2 or X3:
                                if x == j:
                                    if not (connection.get_eknights(y + y2, x)):
                                        k.move(y + y2, x)
                                    elif (x + 1 < L) and not (connection.get_eknights(y, x + 1)):
                                        k.move(y, x + 1)
                                        X2 += 1
                                        X1 -= 1
                                    elif (x - 1 >= 0) and not (connection.get_eknights(y, x - 1)):
                                        k.move(y, x - 1)
                                        X3 += 1
                                        X1 -= 1
                                    else:
                                        k.target = None
                                        X1 -= 1
                                elif x - j == 1:
                                    if not (connection.get_eknights(y + y2, x)):
                                        k.move(y + y2, x)
                                    elif not (connection.get_eknights(y, x - 1)):
                                        k.move(y, x - 1)
                                        X1 += 1
                                        X2 -= 1
                                    else:
                                        k.target = None
                                        X2 -= 1
                                elif x - j == -1:
                                    if not (connection.get_eknights(y + y2, x)):
                                        k.move(y + y2, x)
                                    elif not (connection.get_eknights(y, x + 1)):
                                        k.move(y, x + 1)
                                        X1 += 1
                                        X3 -= 1
                                    else:
                                        k.target = None
                                        X3 -= 1
                                else:
                                    cl.move_without_suicide(k, eknights, i, j)
                            elif X1 > 1:
                                if x == j:
                                    if (x + 1 < L) and not (connection.get_eknights(y, x + 1)):
                                        k.move(y, x + 1)
                                        X2 += 1
                                        X1 -= 1
                                    elif (x - 1 >= 0) and not (connection.get_eknights(y, x - 1)):
                                        k.move(y, x - 1)
                                        X3 += 1
                                        X1 -= 1
                                    elif not (connection.get_eknights(y + y2, x)):
                                        k.move(y + y2, x)
                                    else:
                                        k.target = None
                                        Y1 -= 1
                            else:
                                cl.move_without_suicide(k, eknights, i, j)
                        elif X2 and X3 and (abs(b) + abs(a) > 2):
                            if x - j == 1:
                                if not (connection.get_eknights(y + y2, x)):
                                    k.move(y + y2, x)
                                elif not (connection.get_eknights(y, x - 1)):
                                    k.move(y, x - 1)
                                    X1 += 1
                                    X2 -= 1
                                else:
                                    k.target = None
                                    X2 -= 1
                            if x - j == -1:
                                if not (connection.get_eknights(y + y2, x)):
                                    k.move(y + x2, x)
                                elif not (connection.get_eknights(y, x + 1)):
                                    k.move(y, x + 1)
                                    X1 += 1
                                    X3 -= 1
                                else:
                                    k.target = None
                                    X3 -= 1
                        elif X2 and X3 and (abs(b) + abs(a) == 2):
                            if (connection.get_kinds_on_coord(k.target.y, k.target.x + x2, id, consts.KNIGHT)):
                                k.used = True
                            else:
                                if x - j == 1:
                                    if not (connection.get_eknights(y + y2, x)):
                                        k.move(y, x + x2)
                                    elif not (connection.get_eknights(y, x - 1)):
                                        k.move(y, x - 1)
                                        X1 += 1
                                        Y2 -= 1
                                    else:
                                        k.target = None
                                        X2 -= 1
                                if x - j == -1:
                                    if not (connection.get_eknights(y + y2, x)):
                                        k.move(y + y2, x)
                                    elif not (connection.get_eknights(y, x + 1)):
                                        k.move(y, x + 1)
                                        X1 += 1
                                        X3 -= 1
                                    else:
                                        k.target = None
                                        X3 -= 1
                        elif X2 or X3:
                            if x - j == 1:
                                if not (connection.get_eknights(y, x - 1)):
                                    k.move(y, x - 1)
                                    X1 += 1
                                    X2 -= 1
                                elif not (connection.get_eknights(y + y2, x)):
                                    k.move(y + y2, x)
                                else:
                                    k.target = None
                                    X2 -= 1
                            if x - j == -1:
                                if not (connection.get_eknights(y, x + 1)):
                                    k.move(y, x + 1)
                                    X1 += 1
                                    X3 -= 1
                                elif not (connection.get_eknights(y + y2, x)):
                                    k.move(y + x2, x)
                                else:
                                    k.target = None
                                    X3 -= 1
                        else:
                            cl.move_without_suicide(k, eknights, i, j)
    connection.get_data(player.id, player.token)
    player.update_ennemi_data()
    epawnsf = player.epawns
    for k in not_used_knights:
        if k.target is None:
            continue
        dist = 2
        for ep in epawnsf:
            dist2 = (abs(ep.x - k.target.x) + abs(ep.y - k.target.y))
            if dist2 <= dist:
                dist = dist2
                k.target = ep
        if dist == 2:
            k.target = None
