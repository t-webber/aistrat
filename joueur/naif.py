""" naïve algorithm """

import random as rd
import numpy as np
# from scipy.optimize import linear_sum_assignment as hongrois
import api
import joueur.backbone.client_logic as cl
import joueur.castles as build


def farm(pawns, golds, player, token):
    """ 
    farm gold when possible, else go to nearest avaible gold
    """
    good_gold, bad_gold = cl.clean_golds(golds)
    # simple_gold = golds
    if good_gold and pawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        print(golds)
        print(good_gold)
        gold_location = {}
        gold_location = [(item[0], item[1]) for item in good_gold]
        vus = []
        # je fais bouger les peons vers leur mine d'or
        for p, g in cl.hongrois_distance(pawns, gold_location):
            vus.append(pawns[p])
            y, x = pawns[p]
            i, j, _ = good_gold[g]
            if rd.random() > 0.5:  # pour ne pas que le peon aille toujours d'abord en haut puis à gauche
                if x > j:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                elif y > i:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                else:
                    api.farm(y, x, player, token)
            else:
                if y > i:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                elif x > j:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                else:
                    api.farm(y, x, player, token)
        for p in vus:  # j'enlève ceux que je bouge
            pawns.remove(p)


def path_one(units_to_move, other_units):
    '''Cherche le meilleur chemin pour une unité de units_to_move pour voir plus de la map'''
    # print(len(units_to_move))
    maxscore = -float('inf')
    bestpawn = (-1, -1)
    bestmove = (-1, -1)
    for boy in units_to_move:
        moves = api.get_moves(boy[0], boy[1])
        for move in moves:
            new_pawns = [
                other_boy for other_boy in units_to_move if other_boy != boy]
            new_pawns.append(move)
            new_map = api.get_visible(new_pawns+other_units)
            score = cl.visibility_score(new_map, 1/10)
            if score > maxscore:
                maxscore = score
                bestpawn = boy
                bestmove = move
    return bestpawn, bestmove


def path(units_to_move, other_units=[]):
    '''Essaye de chercher un chemin d'exploration optimal pour les units_to_move pour révéler
    le maximum de la carte pour les péons. Prend en compte other_units pour la visibilité'''
    results = []
    # print("Entrées : ",units_to_move)
    for _ in range(len(units_to_move)):
        bestpawn, bestmove = path_one(units_to_move, other_units)
        results.append((bestpawn, bestmove))
        other_units.append(bestpawn)
        units_to_move = [units_to_move[i] for i in range(
            len(units_to_move)) if units_to_move[i] is not bestpawn]
    #     print('Units updated : ',units_to_move)
    # print("Résultats de path : ",results)
    return results


def explore(pawns, player, token):
    """ 
    call on farm for every player
    """
    print("J'explore")
    moves=path(pawns)
    print(moves)
    for one_move in moves:
        api.move(api.PAWN,one_move[0][0],one_move[0][1],one_move[1][0],one_move[1][1],player,token)
    #dico = {'A': [(0, 1), (1, 0)], 'B': [(0, -1), (-1, 0)]}
        #for y, x in pawns:
        #moves = []
        # moves_p = api.get_moves(y, x)
        # for i, j in moves_p:
        #     if (i-y, j-x) in dico[player]:
        #         moves.append((i, j))
        # if moves:
        #     i, j = rd.choice(moves)
        #     api.move(api.PAWN, y, x, i, j, player, token)
        # else:
        #     i, j = rd.choice(moves_p)
        #     api.move(api.PAWN, y, x, i, j, player, token)


def move_defense(defense, pawns, player, token):
    """
    Moves the knights according to their attributed pawn to defend.

    Args:
        hongroise: result of hungarian method on pawns and defense
        defense (list): A list of tuples representing the position of defense unit that havent moved already
        pawns (list): A list of tuples representing the positions of the pawns.
        player (string): describes the playing player
        token (str): A token representing the player

    Returns
        defense knight that still need to move
    """
    hongroise = cl.hongrois_distance(defense, pawns)
    for d, p in hongroise:
        xd, yd = defense[d]
        xp, yp = pawns[p]
        restant = defense.copy()

        if rd.random() > 0.5:  # pour ne pas que le defenseur aille toujours d'abord en haut puis à gauche
            if xd > xp:
                api.move(api.KNIGHT, yd, xd, yd, xd - 1, player, token)
            elif xd < xp:
                api.move(api.KNIGHT, yd, xd, yd, xd + 1, player, token)
            elif yd > yp:
                api.move(api.KNIGHT, yd, xd, yd - 1, xd, player, token)
            elif yd < yp:
                api.move(api.KNIGHT, yd, xd, yd + 1, xd, player, token)
        else:
            if yd > yp:
                api.move(api.PAWN, yd, xd, yd - 1, xd, player, token)
            elif yd < yp:
                api.move(api.PAWN, yd, xd, yd + 1, xd, player, token)
            elif xd > xp:
                api.move(api.PAWN, yd, xd, yd, xd - 1, player, token)
            elif xd < xp:
                api.move(api.PAWN, yd, xd, yd, xd + 1, player, token)

        restant.remove(defense[p])
        return restant


def defend(pawns, defense, eknights, player, token):
    """
    Defends the pawns using the defense strategy against enemy knights.

    Args:
        pawns (list): A list of tuples representing the positions of the pawns.
        defense (list): A list of tuples representing the positions of the defense units.
        eknights (list): A list of tuples representing the positions of the enemy knights.
        token (str): A token representing the player.

    Returns:
        None
    """
    needing_help = [[], [], []]

    for i in range(len(pawns)):
        for j in range(len(eknights)):
            (x1, y1), (x2, y2) = pawns[i], eknights[j]
            d = cl.distance(x1, y1, x2, y2)
            if (d < 3):
                needing_help[d] = (x1, y1)

    # on priorise les pions selon la distance à un chevalier ennemi
    left_defense = move_defense(defense, needing_help[0], player, token)
    left_defense = move_defense(left_defense, needing_help[1], player, token)
    left_defense = move_defense(left_defense, needing_help[2], player, token)
    return left_defense


def nexturn(player, token):
    """ 
    run next turn for the current player 
        - build a castle
        - farm coins
    """
    kinds = api.get_kinds(player)
    pawns: list[api.Coord] = kinds[api.PAWN]
    knights: list[api.Coord] = kinds[api.KNIGHT]
    eknights: list[api.Coord] = kinds[api.EKNIGHT]
    # liste des chevaliers attribués à la défense
    defense: list[api.Coord] = kinds[api.KNIGHT]
    golds: list[api.Coord] = kinds[api.GOLD]
    castles: list[api.Coord] = kinds[api.CASTLE]

    # pour moi, on appelle dans l'ordre :
    # fuite qui dit au peons de fuire s'ils vont se faire tuer
    # (i.e un méchant est à côté et pas de gentil assez près pour l'aider)
    # construction forteresse
    # farm
    # explore
    # defense/attaque
    build.create_pawns(castles, player, token, eknights, knights)
    build.check_build(pawns, castles, player, token)
    farm(pawns, golds, player, token)  # je farm d'abord ce que je vois
    # j'explore ensuite dans la direction opposée au spawn
    explore(pawns, player, token)


# class gold:

#     def __init__(self) -> none:
#         self.cases = {}

#     def actualiser(self, golds):
#         for i, j, g in golds:
#             self.cases[(i, j)] = g


# class seen:

#     def __init__(self) -> none:
#         self.cases = {}
#         y, x = api.size_map()
#         for y in range(y):
#             for x in range(x):
#                 self.cases[(y, x)] = np.inf

#     def actualiser(self, seen):
#         for pos in self.cases:
#             self.cases[pos] += 1
#         for (y, x) in seen:
#             self.cases[(y, x)] = 0
