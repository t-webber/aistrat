""" fonctions globales disponibles pour toutes les strategie """

from scipy.optimize import linear_sum_assignment
import numpy as np
from apis import connection
from apis.kinds import Unit

defense_knights = {"A": [], "B": []}


def move_defender(y, x, ny, nx, player):
    for i in range(len(defense_knights[player])):
        if defense_knights[player][i] == (y, x):
            defense_knights[player][i] = (ny, nx)
            return


def visibility_score(carte, punishment=0):
    '''Permet de donner un score à une carte de visibilité
    Punishment représente le nombre de points retirés par sur-visibilité qu'on préfèrera sûrement garder à 0
    (on le veut pas trop grand pour favoriser l'exploration)'''
    score = 0
    for row in carte:
        for square in row:
            if square == 1:
                score += 1
            if square > 1:
                score = score+1-(square-1)*punishment
                # Ligne arbitraire -> Combien retirer de point par case "sur-visible"
    return score


def distance(x1, y1, x2, y2):
    """
    calcule la distance de Manhattan entre (x1, y1) et (x2, y2).

    Parametres:
        x1, y1 : les coordonées du premier point.
        x2, y2 : Les coordonées du second point.
    """
    return abs(x1 - x2) + abs(y1 - y2)


def distance_to_list(current_position: connection.Coord, list_positions: list[connection.Coord]):
    """ donne la distance au château le plus proche """
    d = float('inf')
    y_curr, x_curr = current_position
    for (y, x) in list_positions:
        d = min(distance(y, x, y_curr, x_curr), d)
    return d


def exists_close(current_position: connection.Coord, list_targets: list[connection.Coord], sep: int) -> bool:
    """ Check if there is a target close to the current position """
    y_curr, x_curr = current_position
    for (y, x) in list_targets:
        if distance(y, x, y_curr, x_curr) <= sep:
            return True
    return False


def hongrois_distance(acteurs, objets):
    """
    Calcule la distance hongroise entre  les acteurs et objets donnés.

    Parametres:
        acteurs: liste des acteurs.
        objets: liste des objets.
    """
    matrice_cost = np.abs(
        np.array(acteurs)[:, np.newaxis] - np.array(objets)).sum(axis=2)
    return (algo_hongrois(matrice_cost), acteurs)


def clean_golds(golds, pawns, ecastles):
    """
    Donne la priorité aux grosses piles à côté d'autres petites piles et n'envoie qu'un péon.

    Args:
        golds: liste des piles d'or, ou chaque pile est représenté par le tuple (x, y, quantité).

    Returns: list of gold piles after removing the close piles.
    """
    threshold_bad = 16
    distance_overlook = 1
    to_be_removed = [0 for _ in range(len(golds))]
    for num, pile in enumerate(golds):
        if pile[2] <= threshold_bad and to_be_removed[num] == 0:
            for i, gold in enumerate(golds):
                if i != num and ((pile[0], pile[1]) not in pawns) and to_be_removed[i] == 0 \
                        and distance(pile[0], pile[1], gold[0], gold[1]) <= distance_overlook:
                    to_be_removed[num] = 1
                    break
    gold_clean = []
    gold_bad = []
    for i, pile_remove in enumerate(to_be_removed):
        if golds[i][0:2] in ecastles:
            continue
        if pile_remove == 0:
            gold_clean.append(golds[i])
        else:
            gold_bad.append(golds[i])
    return (gold_clean, gold_bad)


def algo_hongrois(matrice_hongrois):
    """
    Applique la méthode hongroise pour résoudre le problème d'assignation.

    Args:
        matrice_hongrois (numpy.ndarray): La matrice de cout représentant le problème.

    Returns: objet zip contenant les indices des colonnes et lignes assignées.
    """
    a, b = linear_sum_assignment(matrice_hongrois)
    return zip(a, b)


def prediction_combat(a, d):
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
        pertes_a += min(a, (d + 1)//2)
        a = a - (d + 1)//2
        pertes_d += min(d, (a + 1)//2)
        d = d - (a + 1)//2
    return (d <= 0, pertes_a <= pertes_d, pertes_a, pertes_d)


def neighbors(case, knights):
    """
    renvoie un couple avec :
    1 : une liste contenant les 4 listes contenant les unités sur cette case (sens trigo, droite en premier)
    2 : renvoie le nombre de chevaliers ennemis dans les quatres case adjacentes à une case
    """
    dir_case = {(0, 1): [], (1, 0): [], (0, -1): [], (-1, 0): []}
    for k in knights:
        if (k.y-case[0], k.x-case[1]) in dir_case:
            dir_case[(k.y-case[0], k.x-case[1])].append(k)
    return dir_case, sum(len(dir_case[d]) for d in dir_case)


def not_moved(units):
    '''donne les unités n'ayant pas bougé ce tour'''
    units_not_moved = set()
    for unit in units:
        if not unit.used:
            units_not_moved.add(unit)
    return units_not_moved


def find_unit(units: Unit, y: int, x: int):
    """
    find a unit in a list of units by its coordinates
    """
    for unit in units:
        if unit.y == y and unit.x == x:
            return unit
