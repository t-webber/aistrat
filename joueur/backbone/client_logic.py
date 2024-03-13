""" Global functions available for all strategies """

from scipy.optimize import linear_sum_assignment
import numpy as np


def hongrois_distance(acteurs, objets):
    """ hungarian distance computation """
    cost_matrix = np.abs(
        np.array(acteurs)[:, np.newaxis] - np.array(objets)).sum(axis=2)
    return algo_hongrois(cost_matrix)


def algo_hongrois(hungarian_matrix):
    """
    The Hungarian algorithm, also known as the Kuhn-Munkres algorithm, 
    is a method for solving the assignment problem, which is the task of 
    assigning a number of agents to an equal number of tasks while minimizing 
    the total cost or maximizing the total profit. The algorithm starts by 
    creating a cost matrix where each cell represents the cost of assigning 
    a particular agent to a specific task. It then manipulates the matrix 
    through a series of steps including subtracting the smallest value in 
    each row and column from all other values in the same row and column, 
    marking zeros with lines, and adjusting the matrix until all zeros can 
    be covered with a minimum number of lines. The optimal assignment is 
    then found by selecting a set of zeros such that there is exactly one 
    selected zero in each row and each column.
    """
    a, b = linear_sum_assignment(hungarian_matrix)
    return zip(a, b)


def prediction_combat(a, d):
    """ prédit le vainqueur d'un combat

    :return: True if attack is won
    """
    pertes_a = 0
    pertes_d = 0
    while a > 0 and d > 0:
        pertes_a += min(a, (d + 1)//2)
        a = a - (d + 1)//2
        pertes_d += min(d, (a + 1)//2)
        d = d - (a + 1)//2
    return (d <= 0, pertes_a, pertes_d)
