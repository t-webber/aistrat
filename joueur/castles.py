import api


def check_build(pawns, caslte, ):
    if len(castle) >= 1:
        return
    for (y, x) in pawns:
        if x * y >= 9:
            api.build(api.CASTLE, y, x, player, token)
