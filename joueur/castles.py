""" Add castles when needed """

import api


def check_build(pawns, castles, player, token):
    """ Add castles if none built and a pawn is enough away """
    len_y, len_x = api.size_map()
    if len(castles) >= 2:
        return
    for pawn in pawns:
        y, x = pawn
        if 2 <= x <= len_x - 3 and 2 <= y <= len_y - 3:
            print("Building caste at", y, x)
            res = api.build(api.CASTLE, y, x, player, token)
            if res:
                pawns.remove(pawn)
            return


def create_pawns(castles, player, token):
    """ Create pawns on every castle """
    for (y, x) in castles:
        api.build(api.PAWN, y, x, player, token)
