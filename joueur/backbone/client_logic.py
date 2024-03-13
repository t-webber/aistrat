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

def cleanGolds(golds): #Priorise les petits tas à côté des gros tas et n'y envoie qu'un seul péon
    toBeRemoved=[0 for _ in range(len(golds))]
    for num in range(len(golds)):
        pile=golds[num]
        if pile[2]<16 and toBeRemoved[num]==0:
            for i in range(len(golds)):
                if i!=num and distance(pile[0],pile[1],golds[i][0],golds[i][1])<=1:
                    toBeRemoved[i]=1
    goldClean=[golds[i] for i in range(len(golds)) if toBeRemoved[i]==0]
    print(golds,goldClean,toBeRemoved)
    return goldClean


def prediction_combat(a, d):  # prédit le vainqueur d'un combat
    pertes_a = 0
    pertes_d = 0
    while a > 0 and d > 0:
        pertes_a += min(a,(d + 1)//2)
        a = a - (d + 1)//2
        pertes_d += min(d,(a + 1)//2)
        d = d - (a + 1)//2
    return (d <= 0, pertes_a, pertes_d)  # true si l'attaque gagne
