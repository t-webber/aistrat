""" Global functions available for all strategies """

from scipy.optimize import linear_sum_assignment
import numpy as np

def distance(x1, y1, x2, y2):
    """ 
    distance between coordinates
    """
    return abs(x1-x2)+abs(y1-y2)

def hongroisDistance(acteurs,objets):
    matriceCost= np.abs(np.array(acteurs)[:, np.newaxis] - np.array(objets)).sum(axis=2)
    return algoHongrois(matriceCost)

def algoHongrois(matriceHongrois):
    a,b=linear_sum_assignment(matriceHongrois)
    return zip(a,b)

def prediction_combat(a, d):  # prédit le vainqueur d'un combat
    pertes_a = 0
    pertes_d = 0
    while a > 0 and d > 0:
        pertes_a += min(a, (d + 1)//2)
        a = a - (d + 1)//2
        pertes_d += min(d, (a + 1)//2)
        d = d - (a + 1)//2
    return (d <= 0, pertes_a, pertes_d)
