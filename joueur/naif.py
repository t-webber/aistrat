import api
import random as rd
from scipy.optimize import linear_sum_assignment
import numpy as np

def distance(x1,y1,x2,y2):
    return abs(x1-x2)+abs(y1-y2)

def farm(pawns,golds, player, token):
    if golds and pawns :
        # affecation problem
        cost = np.abs(np.array(pawns)[:, np.newaxis] - np.array(golds)).sum(axis=2)
        pawn_ind, gold_ind = linear_sum_assignment(cost)

        vus = []
        for p, g in zip(pawn_ind, gold_ind):
            vus.append(pawns[p])
            y, x = pawns[p]
            i, j = golds[g]
            if rd.random() > 0.5:
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
        for p in vus:
            pawns.remove(p)

def explore(pawns, player, token):
    dico = {'A': [(0, 1), (1, 0)], 'B': [(0, -1), (-1, 0)]}
    for y,x in pawns:
        moves = []
        moves_p = api.getMoves(y, x)
        for i, j in moves_p:
            if (i-y, j-x) in dico[player]:
                moves.append((i, j))
        if moves:
            i, j = rd.choice(moves)
            api.move(api.PAWN, y, x, i, j, player, token)
        else:
            i, j = rd.choice(moves_p)
            api.move(api.PAWN, y, x, i, j, player, token)



def nexturn(player,token):
    kinds = api.getKinds(player)
    pawns = kinds[api.PAWN]
    golds = kinds[api.GOLD]
    farm(pawns, golds, player, token)
    explore(pawns, player, token)