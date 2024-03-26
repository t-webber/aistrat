""" global functions available for all strategies """

from scipy.optimize import linear_sum_assignment
import numpy as np

defense_knights=[]
attack_knights=[]

def move_attack(x,y,nx,ny):
    for knight in attack_knights:
        if knight==(x,y):
            knight=(nx,ny)

def move_defense (x,y,nx,ny):
    for knight in defense_knights:
        if knight==(x,y):
            knight=(nx,ny)
            
def visibility_score(carte,punishment):
    '''Permet de donner un score à une carte de visibilité
    Punishment représente le nombre de points retirés par sur-visibilité
    (on le veut pas trop grand pour favoriser l'exploration)'''
    score=0
    for row in carte:
        for square in row:
            if square==1:
                score+=1
            if square>1:
                score=score+1-(square-1)*punishment
                #Ligne arbitraire -> Combien retirer de point par case "sur-visible"
    return score

def distance(x1, y1, x2, y2):
    """
    Calculates the Manhattan distance between two points (x1, y1) and (x2, y2).

    Parameters:
        x1, y1 : The coordinates of the first point.
        x2, y2 : The coordinates of the second point.
    """
    return abs(x1 - x2) + abs(y1 - y2)


def hongrois_distance(acteurs, objets):
    """
    Calculates the Hungarian distance between the given actors and objects.

    Parameters:
        acteurs: list of actors.
        objets: list of objects.
    """
    matrice_cost = np.abs(
        np.array(acteurs)[:, np.newaxis] - np.array(objets)).sum(axis=2)
    return algo_hongrois(matrice_cost)


def clean_golds(golds,pawns):
    """
    Gives the priority to the big piles near other small piles, and sends only one pawn.

    Args:
        golds: list of gold piles, where each pile is represented as a tuple (x, y, amount).

    Returns: list of gold piles after removing the close piles.
    """
    threshold_bad=16
    distance_overlook=1
    to_be_removed = [0 for _ in range(len(golds))]
    for num in range(len(golds)) :
        pile = golds[num]
        if pile[2] <= threshold_bad and to_be_removed[num] == 0:
            for i in range(len(golds)):
                if i != num and ((pile[0],pile[1]) not in pawns) and to_be_removed[i]==0 and distance(pile[0], pile[1], golds[i][0], golds[i][1]) <= distance_overlook:
                    to_be_removed[num] = 1
                    break
    gold_clean = []
    gold_bad = []
    for i in range(len(to_be_removed)):
        if to_be_removed[i]==0:
            gold_clean.append(golds[i])
        else: 
            gold_bad.append(golds[i])
    return (gold_clean,gold_bad)


def algo_hongrois(matrice_hongrois):
    """
    Applies the Hungarian algorithm to solve the assignment problem.

    Args:
        matrice_hongrois (numpy.ndarray): The cost matrix representing the assignment problem.

    Returns: zip object containing the indices of the assigned rows and columns.
    """
    a, b = linear_sum_assignment(matrice_hongrois)
    return zip(a, b)


def prediction_combat(a, d):
    """
    Predicts the winner of a combat

    Parameters:
        a (int): Force of attacker.
        d (int): Force du defender.

    Returns: tuple (bool, int, int) where:
        - bool: True if the attacker wins, False otherwise.
        - int: Number of losses for the attacker.
        - int: Number of losses for the defender.
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
    return the number of knights in the 4 directions of a case
    """
    dir_case = {(0,1):0,(1,0):0,(0,-1):0,(-1,0):0}
    for k in knights:
        if (k[0]-case[0],k[1]-case[1]) in dir_case:
            dir_case[(k[0]-case[0],k[1]-case[1])] +=1
    return dir_case, sum(dir_case.values())