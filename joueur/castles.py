""" Add castles when needed """

import api
import joueur.backbone.client_logic as cl


def distance_2_castle(y_curr, x_curr, castles):
    """ Get the distance to the nearest castle """
    d = float('inf')
    for (y, x) in castles:
        d = min(cl.distance(y, y_curr, x, x_curr), d)
    return d


def check_build(pawns, castles, player, token):
    """ Add castles if none built and a pawn is enough away """
    len_y, len_x = api.size_map()
    if len(castles) >= 3:
        return
    for pawn in pawns:
        y, x = pawn
        if 2 <= x <= len_x - 3 and 2 <= y <= len_y - 3 and distance_2_castle(y, x, castles) > 3:
            print("Building caste at", y, x)
            res = api.build(api.CASTLE, y, x, player, token)
            if res:
                pawns.remove(pawn)
            return


def create_pawns(castles, player, token, eknight, knight):
    """ Create pawns on every castle """
    n = abs(2 * len(eknight) - len(knight))
    gold = api.get_gold()
    for (y, x) in castles:
        if n > 0 or gold > 40:
            api.build(api.KNIGHT, y, x, player, token)
            n -= 1
        else:
            api.build(api.PAWN, y, x, player, token)
