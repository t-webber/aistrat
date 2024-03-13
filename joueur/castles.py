""" Add castles when needed """

import api


def check_build(pawns, castles, player, token):
    """ Add castles if none built and a pawn is enough away """
    if len(castles) >= 1:
        return
    for (i, (x, y)) in enumerate(pawns):
        if x * y >= 9:
            api.build(api.CASTLE, y, x, player, token)
            pawns.remove(i)
            return
