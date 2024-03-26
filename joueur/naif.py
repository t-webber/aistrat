""" naïve algorithm """

import random as rd
import numpy as np
# from scipy.optimize import linear_sum_assignment as hongrois
import api
import joueur.backbone.client_logic as cl
import joueur.castles as build
import joueur.backbone.attaque as atk


def fuite(pawns, knights, eknights, defense, player, token):
    for p in pawns:
        dir_enemies, total_enemies = cl.neighbors(p, eknights)
        dir_allies, allies_backup = cl.neighbors(p, knights)
        allies = 0
        for k in knights:
            if k[0] == p[0] and k[1] == p[1]:
                allies += 1
        for k in defense:
            if k[0] == p[0] and k[1] == p[1]:
                allies += 1

        if not cl.prediction_combat(allies+allies_backup, total_enemies):
            # si on peut perd le combat même avec les alliés on fuit
            for dir in dir_enemies:
                if dir_enemies[dir] == 0:
                    api.move(api.PAWN, p[0], p[1], p[0] +
                             dir[0], p[1]+dir[1], player, token)
                    pawns.remove((p[0], p[1]))
                    break
        else:
            # on peut réussir à gagner le combat avec les alliés et on le fait venir
            while not cl.prediction_combat(allies, total_enemies) and allies_backup > 0:
                for dir in dir_allies:
                    if dir_allies[dir] > 0:
                        api.move(
                            api.KNIGHT, p[0]+dir[0], p[1]+dir[1], p[0], p[1], player, token)
                        knights.remove((p[0]+dir[0], p[1]+dir[1]))
                        allies_backup -= 1
                        break


def farm(pawns, golds, player, token, good_gold, bad_gold, eknights):
    """ 
    farm gold when possible, else go to nearest avaible gold
    """

    # simple_gold = golds
    if good_gold and pawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        # # printgolds)
        # # printgood_gold)
        gold_location = {}
        gold_location = [(item[0], item[1]) for item in good_gold]
        vus = []
        # je fais bouger les peons vers leur mine d'or
        for p, g in cl.hongrois_distance(pawns, gold_location):
            vus.append(pawns[p])
            y, x = pawns[p]
            i, j, _ = good_gold[g]
            if rd.random() > 0.5:  # pour ne pas que le peon aille toujours d'abord en haut puis à gauche
                if x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                elif y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                else:
                    api.farm(y, x, player, token)
            else:
                if y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                elif x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                else:
                    api.farm(y, x, player, token)
        for p in vus:  # j'enlève ceux que je bouge
            pawns.remove(p)


def path_one(units_to_move, other_units, eknights):
    '''Cherche le meilleur chemin pour une unité de units_to_move pour voir plus de la map'''
    # # printlen(units_to_move))
    maxscore = -float('inf')
    bestpawn = (-1, -1)
    bestmove = (-1, -1)
    for boy in units_to_move:
        stuck = 0
        moves = api.get_moves(boy[0], boy[1])
        static_units = [
            other_boy for other_boy in units_to_move if other_boy != boy]+other_units
        static_view = api.get_visible(static_units)
        for move in moves:
            new_map = api.add_visible(static_view, move)
            # # printcl.plus_gros_trou(new_map))
            score = cl.visibility_score(new_map)
            if abs(score-maxscore) <= 1:
                stuck += 1
                continue
            if score > maxscore and cl.neighbors(move, eknights)[1] == 0:
                maxscore = score
                bestpawn = boy
                bestmove = move

        # if better==1 and stuck==4:
        #     print("On règle par un trou",boy)
        #     vecteur_trou=np.array((milieu_du_trou[0]-boy[0],milieu_du_trou[1]-boy[1]))
        #     max_trou=-1
        #     bestmove_trou=(0,0)
        #     for move in moves:
        #         vector_move = np.array((move[0]-boy[0], move[1]-boy[1]))
        #         if np.dot(vecteur_trou,vector_move)>max_trou:
        #             bestmove_trou=move
        #     score = cl.visibility_score(api.add_visible(static_view,bestmove_trou))
        #     maxscore = score
        #     bestpawn = boy
        #     bestmove = bestmove_trou
        #     trou_pris=True

    return bestpawn, bestmove


def path_trou(units_to_move, other_units, eknights):
    '''Dirige les péons vers des trous'''
    resultat = []
    # trous=cl.trous(api.get_visible(units_to_move+other_units))
    # trous_tri = sorted(trous, key=lambda x: len(x))
    everybody = units_to_move+other_units
    visibility = api.get_visible(everybody)
    trous_list = cl.trous(visibility)
    for boy in units_to_move:
        print("On règle par un trou", boy)
        milieu_du_trou = cl.plus_proche_trou(trous_list, boy)
        moves = api.get_moves(boy[0], boy[1])
        vecteur_trou = np.array(
            (milieu_du_trou[0]-boy[0], milieu_du_trou[1]-boy[1]))
        max_trou = -1
        bestmove_trou = (0, 0)
        for move in moves:
            vector_move = np.array((move[0]-boy[0], move[1]-boy[1]))
            if np.dot(vecteur_trou, vector_move) > max_trou and cl.neighbors(move, eknights)[1] == 0:
                bestmove_trou = move
        resultat.append((boy, bestmove_trou))
    return resultat


def path(units_to_move, other_units, eknights):
    '''Essaye de chercher un chemin d'exploration optimal pour les units_to_move pour révéler
    le maximum de la carte pour les péons. Prend en compte other_units pour la visibilité'''
    results = []
    # print("Entrées : ",units_to_move)
    strategie = 0
    for i in range(len(units_to_move)):
        if strategie == 0:
            bestpawn, bestmove = path_one(units_to_move, other_units, eknights)
            if bestpawn == (-1, -1):
                strategie = 1
                i -= 1
                continue
            results.append((bestpawn, bestmove))
            other_units.append(bestpawn)
            units_to_move = [units_to_move[i] for i in range(
                len(units_to_move)) if units_to_move[i] is not bestpawn]
        if strategie == 1:
            results = results+path_trou(units_to_move, other_units, eknights)
            break
    #     print('Units updated : ',units_to_move)
    # print("Résultats de path : ",results)
    return results


def explore(pawns, player, token, eknights):
    """ 
    Envoie en exploration les "pawns" inactifs pour le tour
    """
    # print("J'explore")
    moves = path(pawns, [], eknights)
    # print(moves)
    for one_move in moves:
        api.move(api.PAWN, one_move[0][0], one_move[0][1],
                 one_move[1][0], one_move[1][1], player, token)

    # dico = {'A': [(0, 1), (1, 0)], 'B': [(0, -1), (-1, 0)]}
        # for y, x in pawns:
        # moves = []
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


def move_defense(defense, pawns, player, token, eknight):
    """
    Moves the knights according to their attributed pawn to defend.

    Args:
        hongroise: result of hungarian method on pawns and defense
        defense (list): A list of tuples representing the position of defense unit that havent moved already
        pawns (list): A list of tuples representing the positions of the pawns.
        player (string): describes the playing player
        token (str): A token representing the player

    Returns
        defense knights that still need to move
    """
    if(pawns==[] ):
        return defense
    hongroise = cl.hongrois_distance(defense, pawns)
    utilise=[]
    for d, p in hongroise:
        yd, xd = defense[d]
        yp, xp = pawns[p]
        utilise.append(defense[d])
        if rd.random() > 0.5:  # pour ne pas que le defenseur aille toujours d'abord en haut puis à gauche
            if xd > xp and (yd, xd-1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd - 1, player, token)
                cl.move_defender(yd, xd, yd, xd - 1, player)
            elif xd < xp and (yd, xd+1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd + 1, player, token)
                cl.move_defender(yd, xd, yd, xd + 1, player)
            elif yd > yp and (yd-1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd-1, xd, player, token)
                cl.move_defender(yd,xd, yd-1, xd, player)
            elif yd < yp and (yd + 1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd + 1, xd, player, token)
                cl.move_defender(yd, xd, yd+1, xd, player)
        else:
            if yd > yp and (yd - 1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd - 1, xd, player, token)
                cl.move_defender(yd, xd, yd-1, xd, player)
            elif yd < yp and (yd + 1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd + 1, xd, player, token)
                cl.move_defender(yd, xd, yd + 1, xd, player)
            elif xd > xp and (yd, xd - 1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd - 1, player, token)
                cl.move_defender(yd, xd, yd, xd - 1, player)
            elif xd < xp and (yd, xd + 1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd + 1, player, token)
                cl.move_defender(yd, xd, yd, xd + 1, player)

    for d in utilise:
        defense.remove(d)
    return defense


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
    needing_help = [[] for i in range(50)]
    pawns = list(set(pawns.copy()))  # elimination des doublons
    for i in range(len(pawns)):
        for j in range(len(eknights)):
            (y1, x1), (y2, x2) = pawns[i], eknights[j]
            d = cl.distance(x1, y1, x2, y2)
            if (d < 50):
                needing_help[d].append((y1, x1))

    # on priorise les pions selon la distance à un chevalier ennemi
    compteur = 0
    left_defense = defense.copy()
    while (bool(left_defense) and compteur<50):
        rd.shuffle(needing_help[compteur])
        left_defense = move_defense(left_defense, needing_help[compteur], player, token, eknights)
        compteur += 1


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
    epawns: list[api.Coord] = kinds[api.EPAWN]
    fog = kinds[api.FOG]
    # liste des chevaliers attribués à la défense
    defense: list[api.Coord] = cl.defense_knights[player]
    golds: list[api.Coord] = kinds[api.GOLD]
    castles: list[api.Coord] = kinds[api.CASTLE]
    ecastles: list[api.Coord] = kinds[api.ECASTLE]
    try:
        gold = api.get_gold()[player]
    except:
        gold = 0

    # print("FOOOOG", fog)

    # pour moi, on appelle dans l'ordre :
    # defense
    # fuite qui dit au peons de fuire s'ils vont se faire tuer
    # (i.e un méchant est à côté et pas de gentil assez près pour l'aider)
    # construction forteresse
    # farm
    # explore
    # attaque
    for d in defense:
        if d not in knights:
            defense.remove(d)
    #    else:
    #        knights.remove(d)

    good_gold, bad_gold = cl.clean_golds(golds, pawns)

    defend(pawns, defense, eknights, player, token)
    fuite(pawns, knights, eknights, defense, player, token)

    build.create_pawns(castles, player, token,
                       eknights, knights, gold, cl.defense_knights[player],
                       (len(good_gold) + len(bad_gold)), len(pawns), len(fog))

    build.check_build(pawns, castles, player, token, gold)
    farm(pawns, golds, player, token, good_gold, bad_gold,
         eknights)  # je farm d'abord ce que je vois
    # j'explore ensuite dans la direction opposée au spawn
    explore(pawns, player, token, eknights)
    atk.hunt(knights, epawns, eknights, player, token)
    atk.destroy_castle(knights, ecastles, eknights, player, token)

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
