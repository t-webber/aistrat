import random
import api


def nexturn(player, token):
    """
    Perform a random move for a player's pawn.

    Args:
        player (Player): The player making the move.
        token (str): The player's authentication token.

    Returns:
        None

    """
    kinds = api.get_kinds(player)
    for (i, j) in kinds[api.PAWN]:
        y, x = random.choice(api.get_moves(i, j))
        api.move(api.PAWN, i, j, y, x, player, token)
