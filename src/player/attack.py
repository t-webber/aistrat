"""Fonctions pour définir les actions d'un attaquant."""

from apis import connection
from apis.connection import Coord
from apis.kinds import Pawn, Knight, Castle, Enemy
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

        # affecation problem
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
                cl.move_without_suicide(knights_not_used[k], eknights, i, j)


def free_pawn(knights: list[Knight], eknights: list[Knight], epawns: list[Enemy], castles: list[Castle]):
    """Attaque les péons et les chateaux gratuits s'ils sont adjacent à un chevalier libre."""
    for knight in knights:
        if not knight.used:
            for castle in castles:
                if cl.distance(knight.x, knight.y, castle.x, castle.y) == 1 and prediction_attaque((castle.y,castle.x),knights,eknights):
                    a= cl.movable_neighbors(castle.coord, knights)[0]
                    allies_voisins_exploitable = []
                    for e in a:
                        allies_voisins_exploitable += a[e]
                    move_everyone(castle.coord, allies_voisins_exploitable)
        if not knight.used:
            for epawn in epawns:
                if cl.distance(knight.x, knight.y, epawn.x, epawn.y) == 1 and prediction_attaque((epawn.y,epawn.x),knights,eknights):
                    a= cl.movable_neighbors(epawn.coord, knights)[0]
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

def sync_atk(knights: list[Knight], eknights: list[Knight], epawns: list[Enemy]):
    not_used_knights = list(filter(lambda knight: not knight.used, knights))
    dicoattaque = {}
    for ep in epawns:
        dicoattaque[ep]=[]
    for k in not_used_knights:
        epawn = k.target
        dicoattaque[epawn]= dicoattaque[ep] + [k]
    for ep in dicoattaque:
        i,j = ep.coord
        newpos=[]
        for k in dicoattaque[ep]:
            y, x = k.coord
            a = i - y
            b = j - x
            y2 = a/abs(a)
            x2 = b/abs(b)
            if a != 0 and b !=0:
                if not cl.connection.get_eknights(y, x + x2) and (y, x + x2) not in newpos:
                    k.move(y, x + x2)
                    newpos += (y,x + x2)
                elif not cl.connection.get_eknights(y + y2, x) and (y + y2, x) not in newpos:
                    k.move(y + y2, x)
                    newpos += (y + y2,x)
                else:
                    cl.move_without_suicide(k, eknights, i, j)
            else: 
                cl.move_without_suicide(k, eknights, i, j)