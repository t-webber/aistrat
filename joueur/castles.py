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
    """ Build some castle, and, at the beggining, take control of a pawn to build the first castle in the right place  """
    len_y, len_x = api.size_map()

    # define borders to not build castles on the borders
    border = 2
    border_x = len_x - 1 - border
    border_y = len_y - 1 - border

    # adapt side to the player : player A (up left) or player B (down right)
    good = (border, border) if player == "A" else (
        border_y, border_x)

    # if no castles where built, take control of a pawn and put him in (2, 2), then build a castle
    if len(castles) == 0:
        d = distance_2_castle(good[0], good[1], pawns)
        if d != 0:  # if d == 0, the pawn is in the right place so it will build a castle bellow
            for (y, x) in pawns:

                # this pawn is the nearest from the good place
                if cl.distance(y, x, good[0], good[1]) == d:
                    if player == "A":

                        # near enough from the destination in x : move y
                        if x >= border:
                            api.move(api.PAWN, y, x, y +
                                     1, x, player, token)
                        else:  # move x
                            api.move(api.PAWN, y, x, y,
                                     x+1, player, token)
                    else:
                        # near enough from the destination in x : move y
                        if x <= border_x:
                            api.move(api.PAWN, y, x, y -
                                     1, x, player, token)
                        else:  # move x
                            api.move(api.PAWN, y, x, y,
                                     x-1, player, token)
                    pawns.remove((y, x))
                    break

    # if there are enough castles or not enough gold, don't try anything
    if len(castles) >= min(len_y, len_x) // 2 or gold < api.PRICES[api.CASTLE]:
        return

    # build a castle at the first time the pawn is far enough from the existing castles
    for pawn in pawns:
        y, x = pawn
        d = distance_2_castle(y, x, castles)  # distance to the nearest castle

        # if the pawn is far enough from the bortders
        if border <= x <= border_x and border <= y <= border_y and d >= 3:
            api.build(api.CASTLE, y, x, player, token)
            pawns.remove(pawn)
            gold -= api.PRICES[api.CASTLE]
            return


def create_pawns(castles, player, token, eknight, knight, gold, defenders, nb_gold, nb_pawn, nb_fog):
    """ The castles will spawn units here """
    n = 2 * len(eknight) - len(knight)

    for (y, x) in castles:
        # We are under the attack ! Create some defenders !
        if n > 0:
            if api.build(api.KNIGHT, y, x, player, token):
                defenders.append((y, x))
                api.PRICES[api.KNIGHT] -= 1
                n -= 1

        # Too much gold, build some attackers
        elif gold > api.PRICES[api.KNIGHT] * 2 and len(castles) >= 2:
            if api.build(api.KNIGHT, y, x, player, token):
                gold -= api.PRICES[api.KNIGHT]

        # Missing gold, and there is avaible gold on the map (or fog: places we can't see)
        elif gold > api.PRICES[api.PAWN] * 1.25 and nb_gold + nb_fog > nb_pawn:
            api.build(api.PAWN, y, x, player, token)
            gold -= api.PRICES[api.PAWN]
            nb_pawn += 1
