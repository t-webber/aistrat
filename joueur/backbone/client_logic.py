from scipy.optimize import linear_sum_assignment
import numpy as np

def hongroisDistance(acteurs,objets):
    matriceCost= np.abs(np.array(acteurs)[:, np.newaxis] - np.array(objets)).sum(axis=2)
    return algoHongrois(matriceCost)

def algoHongrois(matriceHongrois):
    a,b=linear_sum_assignment(matriceHongrois)
    return zip(a,b)