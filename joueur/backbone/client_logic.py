from scipy.optimize import linear_sum_assignment
import numpy as np


def hongroisDistance(acteurs, objets):
    matrice = np.abs(np.array(acteurs)[:, np.newaxis] - np.array(objets))
    return algoHongrois(matrice)


def algoHongrois(matriceHongrois):
    return zip(linear_sum_assignment(matriceHongrois))


def prediction_combat(a, d):  # prédit le vainqueur d'un combat
    pertes_a = 0
    pertes_b = 0
    while a > 0 and d > 0:
        pertes_a += (d + 1)//2
        pertes_b += (a + 1)//2
        a = a - (d + 1)//2
        d = d - (a + 1)//2
    return (d <= 0, pertes_a, pertes_b)  # true si l'attaque gagne
