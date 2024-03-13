from scipy.optimize import linear_sum_assignment
import numpy as np

def hongroisDistance(acteurs,objets):
    matrice=np.abs(np.array(acteurs)[:, np.newaxis] - np.array(objets))
    return algoHongrois(matrice)

def algoHongrois(matriceHongrois):
    return zip(linear_sum_assignment(matriceHongrois))
