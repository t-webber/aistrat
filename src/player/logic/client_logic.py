""" fonctions globales disponibles pour toutes les strategie """

from scipy.optimize import linear_sum_assignment
import numpy as np
import api as api

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


def distance_to_list(current_position: api.Coord, list_positions: list[api.Coord]):
    """ donne la distance au château le plus proche """
    d = float('inf')
    y_curr, x_curr = current_position
    for (y, x) in list_positions:
        d = min(distance(y, x, y_curr, x_curr), d)
    return d


def hongrois_distance(acteurs, objets):
    """
    Calcule la distance hongroise entre  les acteurs et objets donnés.

    Parametres:
        acteurs: liste des acteurs.
        objets: liste des objets.
    """
    matrice_cost = np.abs(
        np.array(acteurs)[:, np.newaxis] - np.array(objets)).sum(axis=2)
    return algo_hongrois(matrice_cost)


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
    renvoie le nombre de chevaliers ennemis dans les quatres case adjacentes à une case
    """
    dir_case = {(0, 1): 0, (1, 0): 0, (0, -1): 0, (-1, 0): 0}
    for k in knights:
        if (k[0]-case[0], k[1]-case[1]) in dir_case:
            dir_case[(k[0]-case[0], k[1]-case[1])] += 1
    return dir_case, sum(dir_case.values())


def trous(grille):
    '''Cherche tous les lieux avec un éclairage extrêmement faible'''
    sortie = []
    vus = np.zeros((len(grille), len(grille[0])))
    for i, x in enumerate(grille):
        for j, y in enumerate(x):
            if vus[i][j] == 0 and grille[i][j] == 0:
                a_chercher = [(i, j)]
                vus[i][j] = 1
                trou = []
                while len(a_chercher) > 0:
                    pixel = a_chercher.pop()
                    cases_adjacentes = api.get_moves(pixel[0], pixel[1])
                    for case in cases_adjacentes:
                        if grille[case[0]][case[1]] == 0 and vus[case[0]][case[1]] == 0:
                            vus[case[0]][case[1]] = 1
                            a_chercher.append(case)
                    trou.append(pixel)
                sortie.append((trou))
    return sortie


def plus_gros_trou(grille):
    '''Cherche la plus grande surface continue mal éclairée'''
    holes = trous(grille)
    taille_max = 0
    trou_max = holes[0]
    for one_hole in holes:
        nbr_cases_trou = len(one_hole)
        if nbr_cases_trou > taille_max:
            taille_max = nbr_cases_trou
            trou_max = one_hole
    return trou_max


def milieu_trou(trou):
    '''Trouve le milieu d'un trou (arrondi à l'entier inférieur)'''
    i = 0
    j = 0
    for k in trou:
        i += k[0]
        j += k[1]
    milieu = (i//len(trou), j//len(trou))
    return milieu


def plus_proche_trou(list_trous, unit):
    '''Trouve le trou le plus proche de l'unité'''
    joueur = api.current_player()
    if joueur == 'A':
        best = api.map_size
    else:
        best = (0, 0)
    best_dist = float('inf')
    for trou in list_trous:
        milieu = milieu_trou(trou)
        distance_trou = distance(milieu[0], milieu[1], unit[0], unit[1])
        if distance_trou < best_dist:
            best = milieu
            best_dist = distance_trou
    return best
