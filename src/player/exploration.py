"""Fonctions liées au déplacement et a l'exploration."""
import numpy as np
from apis import connection
import logic.client_logic as cl
from apis.kinds import Pawn, Knight, Unit
import apis.players as pl

# def path_simple(coordinate:tuple[int,int],destination:tuple[int,int],player: pl.Player):
#     """Cherche un bon chemin en un déplacement pour une unité"""
#     moves=connection.get_moves(coordinate[0],coordinate[1])
#     best_moves=sorted(moves,key=lambda x:cl.scalar(coordinate,x,destination))
#     for move in best_moves:
#         ennemies = cl.neighbors(move, player.eknights)[1]
#         if ennemies == 0 or ennemies <= len(connection.get_eknights(move[0], move[1])):
#             return move
#     return None

def path_simple(unit,destination:tuple[int,int], eknights : Knight):
    """Cherche un bon chemin en un déplacement pour une unité"""
    moves=connection.get_moves(unit.y,unit.x)
    best_moves=sorted(moves,key=lambda x:cl.scalar((unit.y,unit.x),x,destination))
    for move in best_moves:
        ennemies = cl.neighbors(move, eknights)[1]
        if ennemies == 0 or ennemies <= len(connection.get_eknights(move[0], move[1])):
            return move
    return None

# def path_simple(coord,destination,player):
#     """Cherche un bon chemin en un déplacement pour une unité"""
#     moves=connection.get_moves(unit.y,unit.x)
#     best_moves=sorted(moves,key=lambda x:x[0]*destination[0]+x[1]*destination[1])
#     for move in best_moves:
#         ennemies = cl.neighbors(move, player.eknights)[1]
#         if ennemies == 0 or ennemies <= len(connection.get_eknights(unit.y, unit.x)):
#             return move
#     return best_moves[0]

def path_one(units_to_move: list[Pawn], other_units: list[Pawn], eknights: list[Knight]):
    """Cherche le meilleur chemin pour une unité de units_to_move pour voir plus de la map."""
    maxscore = cl.visibility_score(
        connection.get_visible(units_to_move + other_units))
    bestpawn = (-1, -1)
    bestmove = (-1, -1)
    for boy in units_to_move:
        stuck = 0
        moves = connection.get_moves(boy.y, boy.x) + [(boy.y, boy.x)]
        static_units = [
            other_boy for other_boy in units_to_move if other_boy != boy] + other_units
        for move in moves:
            new_map = connection.get_visible(static_units + [move])
            score = cl.visibility_score(new_map)
            if abs(score - maxscore) <= 1:
                stuck += 1
                continue
            ennemies = cl.neighbors(move, eknights)[1]
            if score > maxscore and (ennemies == 0 or ennemies <= len(connection.get_eknights(boy.y, boy.x))) and connection.get_eknights(move[0], move[1]) == []:
                maxscore = score
                bestpawn = boy
                bestmove = move
    return bestpawn, bestmove


def path_trou(units: list[Unit], other_units: list[Unit], eknights: list[Knight]):
    """Dirige les péons vers des trous."""
    units_to_move = [unit for unit in units if not unit.used]

    resultat = []
    everybody = units_to_move + other_units
    visibility = connection.get_visible(everybody)
    trous_list = trous(visibility)
    for boy in units_to_move:
        milieu_du_trou = plus_proche_trou(trous_list, boy)
        moves = connection.get_moves(boy.y, boy.x)
        vecteur_trou = np.array(
            (milieu_du_trou[0] - boy.y, milieu_du_trou[1] - boy.x))
        max_trou = -1
        bestmove_trou = (0, 0)
        for move in moves:
            vector_move = np.array((move[0] - boy.y, move[1] - boy.x))
            ennemies = cl.neighbors(move, eknights)[1]
            if np.dot(vecteur_trou, vector_move) > max_trou and not connection.get_eknights(move[0], move[1])\
                    and (ennemies == 0 or ennemies <= len(connection.get_eknights(boy.y, boy.x))):
                bestmove_trou = move
        if bestmove_trou != (0, 0):
            resultat.append((boy, bestmove_trou))
    for res in resultat:
        res[0].move(*res[1])


def trous(grille: list[list[int]]):
    """Cherche tous les lieux avec un éclairage extrêmement faible."""
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
                    cases_adjacentes = connection.get_moves(pixel[0], pixel[1])
                    for case in cases_adjacentes:
                        if grille[case[0]][case[1]] == 0 and vus[case[0]][case[1]] == 0:
                            vus[case[0]][case[1]] = 1
                            a_chercher.append(case)
                    trou.append(pixel)
                sortie.append((trou))
    return sortie


def plus_gros_trou(grille: list[list[int]]):
    """Cherche la plus grande surface continue mal éclairée."""
    holes = trous(grille)
    taille_max = 0
    trou_max = holes[0]
    for one_hole in holes:
        nbr_cases_trou = len(one_hole)
        if nbr_cases_trou > taille_max:
            taille_max = nbr_cases_trou
            trou_max = one_hole
    return trou_max


def milieu_trou(trou: list[tuple[int, int]]):
    """Trouve le milieu d'un trou (arrondi à l'entier inférieur)."""
    i = 0
    j = 0
    for k in trou:
        i += k[0]
        j += k[1]
    milieu = (i // len(trou), j // len(trou))
    return milieu


def plus_proche_trou(list_trous: list[list[tuple[int, int]]], unit: Pawn):
    """Trouve le trou le plus proche de l'unité."""
    joueur = connection.current_player()
    if joueur == 'A':
        best = connection.MAP_SIZE
    else:
        best = (0, 0)
    best_dist = float('inf')
    for trou in list_trous:
        milieu = milieu_trou(trou)
        distance_trou = cl.distance(milieu[0], milieu[1], unit.y, unit.x)
        if distance_trou < best_dist:
            best = milieu
            best_dist = distance_trou
    return best
