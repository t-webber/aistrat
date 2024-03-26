""" Add castles when needed """

import api
import joueur.backbone.client_logic as cl


def distance_2_castle(y_curr, x_curr, castles):
    """ Get the distance to the nearest castle """
    d = float('inf')
    for (y, x) in castles:
        d = min(cl.distance(y, x, y_curr, x_curr), d)
    return d


def check_build(pawns, castles, player, token, gold):
    """ Add castles if none built and a pawn is enough away """
    len_y, len_x = api.size_map()
    good = (2, 2) if player == "A" else (len_y - 3, len_x - 3)
    if len(castles) == 0:
        d = distance_2_castle(good[0], good[1], pawns)
        if d != 0:
            for (y, x) in pawns:
                if cl.distance(y, x, good[0], good[1]) == d:
                    if player == "A":
                        if x >= 2:
                            api.move(api.PAWN, y, x, y +
                                     1, x, player, token)
                        else:
                            api.move(api.PAWN, y, x, y,
                                     x+1, player, token)
                    else:
                        if x <= len_x - 3:
                            api.move(api.PAWN, y, x, y -
                                     1, x, player, token)
                        else:
                            api.move(api.PAWN, y, x, y,
                                     x-1, player, token)
                    pawns.remove((y, x))
                    break

    # print("CHECKING BUILD on ", castles, "PLA", player)
    if len(castles) >= min(len_y, len_x) // 2 or gold < api.PRICES[api.CASTLE]:
        return
    for pawn in pawns:
        y, x = pawn
        d = distance_2_castle(y, x, castles)
        if 2 <= x <= len_x - 3 and 2 <= y <= len_y - 3 and d >= 3:
            # print("Building caste at", y, x)
            api.build(api.CASTLE, y, x, player, token)
            pawns.remove(pawn)
            gold -= api.PRICES[api.CASTLE]
            return


def create_pawns(castles, player, token, eknight, knight, gold, defenders, diff_len):
    """ Create pawns on every castle """
    n = 2 * len(eknight) - len(knight)
    for (y, x) in castles:
        # print("GOOOOOOOOOOOLD", gold)
        if n > 0:
            if api.build(api.KNIGHT, y, x, player, token):
                defenders.append((y, x))
                api.PRICES[api.KNIGHT] -= 1
                n -= 1
        elif gold > api.PRICES[api.KNIGHT] * 2 and len(castles) >= 2:
            if api.build(api.KNIGHT, y, x, player, token):
                gold -= api.PRICES[api.KNIGHT]
        elif gold > api.PRICES[api.PAWN] * 2 and diff_len > 0:
            api.build(api.PAWN, y, x, player, token)
            gold -= api.PRICES[api.PAWN]
