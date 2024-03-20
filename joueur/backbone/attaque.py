import api

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

def compte_soldats_cases_adjacentes(player,case):
    Y,X=case
    carte=api.get_map()
    voisins = api.get_moves(Y,X)
    knight = 0
    eknight = 0
    for c in voisins:
        knight += carte[Y + c[0]][X + c[1]][player][api.KNIGHT]
        eknightknight += carte[Y + c[0]][X + c[1]][player][api.EKNIGHT]
    return (knight, eknight)

    
def attaque(player,case_attaquee):
    carte=api.get_map
    Y,X=case_attaquee
    attaquants, defenseurs_voisins = compte_soldats_cases_adjacentes(player,case_attaquee)
    defenseurs = carte[Y][X][player][api.EKNIGHT]
    b1,b2,pertes_attaque,pertes_defense = prediction_combat(attaquants,defenseurs)
    if b1 and b2:
        attaquants -= pertes_attaque
        defenseurs = defenseurs_voisins
        b1,b2,pertes_attaque2,pertes_defense2 = prediction_combat(attaquants,defenseurs)
        if (pertes_attaque + pertes_attaque2) > (pertes_defense + pertes_defense2):
            api.move(,,,case_attaquee[0],case_attaquee[1],,)