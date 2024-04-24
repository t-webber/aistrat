import random as rd
import numpy as np
import api
import player.logic.client_logic as cl


def fuite(pawns, knights, eknights, defense, player, token):
    i = 0
    while i < len(pawns):
        p = pawns[i]
        i += 1
        direc_enemies, total_enemies = cl.neighbors(p, eknights)
        if total_enemies > 0:
            direc_allies, allies_backup = cl.neighbors(p, knights)
            allies = 0
            allies_defense = 0
            for k in defense:
                if k[0] == p[0] and k[1] == p[1]:
                    allies_defense += 1
                    allies += 1
            for k in knights:
                if k[0] == p[0] and k[1] == p[1]:
                    allies += 1
            
            if cl.prediction_combat(total_enemies, allies+allies_backup)[0]:
                # si on perd le combat même avec les alliés on fuit
                for (direc, nb) in direc_enemies.items():
                    if nb == 0 and (p[0] + direc[0], p[1]+direc[1]) in api.get_moves(p[0], p[1]) and cl.neighbors((p[0] + direc[0], p[1]+direc[1]), eknights)[1] == 0:
                        api.move(api.PAWN, p[0], p[1], p[0] +
                                 direc[0], p[1]+direc[1], player, token)
                        pawns.remove((p[0], p[1]))
                        i -= 1
                        break
            else:
                while cl.prediction_combat(total_enemies, allies_defense)[0] and allies - allies_defense > 0:
                    knights.remove((p[0], p[1]))
                    allies_defense+=1
                # on peut réussir à gagner le combat avec les alliés et on le fait venir
                while cl.prediction_combat(total_enemies, allies)[0] and allies_backup > 0:
                    for direc, nb in direc_allies.items():
                        if nb > 0:
                            api.move(
                                api.KNIGHT, p[0]+direc[0], p[1]+direc[1], p[0], p[1], player, token)
                            
                            if (p[0]+direc[0], p[1]+direc[1]) in knights:
                                knights.remove((p[0]+direc[0], p[1]+direc[1]))
                            allies_backup -= 1
                            allies += 1
                            direc_allies[direc] -= 1
                            break


def farm(pawns, player, token, good_gold, eknights, ecastles):
    """ 
    récolte l'or quand c'est possible, sinon ce déplace vers la pile disponible la plus proche
    """
    
    # simple_gold = golds
    if good_gold and pawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        gold_location = []
        gold_location = [(item[0], item[1]) for item in good_gold]
        vus = []
        # je fais bouger les peons vers leur mine d'or
        for p, g in cl.hongrois_distance(pawns, gold_location):
            vus.append(pawns[p])
            y, x = pawns[p]
            i, j, _ = good_gold[g]
            gold_location.remove((i, j))
            if rd.random() > 0.5:  # pour ne pas que le peon aille toujours d'abord en haut puis à gauche
                if x > j and (y, x - 1) not in eknights and (y, x - 1) not in ecastles and (cl.neighbors((y, x - 1), eknights)[1] == 0 or cl.neighbors((y, x - 1), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j and (y, x + 1) not in eknights and (y, x + 1) not in ecastles and (cl.neighbors((y, x + 1), eknights)[1] == 0 or cl.neighbors((y, x + 1), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                elif y > i and (y - 1, x) not in eknights and (y - 1, x) not in ecastles and (cl.neighbors((y - 1, x), eknights)[1] == 0 or cl.neighbors((y-1, x), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i and (y + 1, x) not in eknights and (y + 1, x) not in ecastles and (cl.neighbors((y + 1, x), eknights)[1] == 0 or cl.neighbors((y+1, x), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                else:
                    api.farm(y, x, player, token)
            else:
                if y > i and (y - 1, x) not in eknights and (y - 1, x) not in ecastles and (cl.neighbors((y - 1, x), eknights)[1] == 0 or cl.neighbors((y-1, x), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i and (y + 1, x) not in eknights and (y + 1, x) not in ecastles and (cl.neighbors((y + 1, x), eknights)[1] == 0 or cl.neighbors((y+1, x), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                elif x > j and (y, x - 1) not in eknights and (y, x - 1) not in ecastles and (cl.neighbors((y, x - 1), eknights)[1] == 0 or cl.neighbors((y, x - 1), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j and (y, x + 1) not in eknights and (y, x + 1) not in ecastles and (cl.neighbors((y, x + 1), eknights)[1] == 0 or cl.neighbors((y, x + 1), eknights)[1] <= len(api.get_defenders(y, x))):
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                else:
                    api.farm(y, x, player, token)
        for p in vus:  # j'enlève ceux que je bouge
            pawns.remove(p)


def path_one(units_to_move, other_units, eknights):
    '''Cherche le meilleur chemin pour une unité de units_to_move pour voir plus de la map'''
    maxscore = cl.visibility_score(api.get_visible(units_to_move+other_units))
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
            score = cl.visibility_score(new_map)
            if abs(score-maxscore) <= 1:
                stuck += 1
                continue
            ennemies = cl.neighbors(move, eknights)[1]
            # print(ennemies)
            if score > maxscore and (ennemies == 0
                                     or ennemies <= len(api.get_defenders(boy[0], boy[1]))):
                maxscore = score
                bestpawn = boy
                bestmove = move

    return bestpawn, bestmove


def path_trou(units_to_move, other_units, eknights):
    '''Dirige les péons vers des trous'''
    resultat = []
    everybody = units_to_move+other_units
    visibility = api.get_visible(everybody)
    trous_list = cl.trous(visibility)
    for boy in units_to_move:
        milieu_du_trou = cl.plus_proche_trou(trous_list, boy)
        moves = api.get_moves(boy[0], boy[1])
        vecteur_trou = np.array(
            (milieu_du_trou[0]-boy[0], milieu_du_trou[1]-boy[1]))
        max_trou = -1
        bestmove_trou = (0, 0)
        for move in moves:
            vector_move = np.array((move[0]-boy[0], move[1]-boy[1]))
            ennemies = cl.neighbors(move, eknights)[1]
            if np.dot(vecteur_trou, vector_move) > max_trou \
                    and (ennemies == 0 or ennemies <= len(api.get_defenders(boy[0], boy[1]))):
                bestmove_trou = move
        resultat.append((boy, bestmove_trou))
    return resultat


def path(units_to_move, other_units, eknights):
    '''Essaye de chercher un chemin d'exploration optimal pour les units_to_move pour révéler
    le maximum de la carte pour les péons. Prend en compte other_units pour la visibilité'''
    results = []
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
        else:
            return (results, units_to_move)
    return (results, units_to_move)


def explore(pawns, player, token, eknights, ecastles, otherunits=[], reste_gold=()):
    """ 
    Envoie en exploration les "pawns" inactifs pour le tour
    """
    moves, remaining_pawns = path(pawns, otherunits, eknights)
    for one_move in moves:
        api.move(api.PAWN, one_move[0][0], one_move[0][1],
                 one_move[1][0], one_move[1][1], player, token)
    if len(reste_gold) > 0:
        farm(remaining_pawns, player, token, reste_gold, eknights, ecastles)
    if len(remaining_pawns) > 0:
        moves_trou = path_trou(remaining_pawns, otherunits, eknights)
        for one_move in moves_trou:
            api.move(api.PAWN, one_move[0][0], one_move[0][1],
                     one_move[1][0], one_move[1][1], player, token)
