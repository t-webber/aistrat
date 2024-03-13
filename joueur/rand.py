import api
import random


def nexturn(player, token):
    kinds = api.getKinds(player)
    for (i, j) in kinds[api.PAWN]:
        y, x = random.choice(api.getMoves(i, j))
        api.move(api.PAWN, i, j, y, x, player, token)
