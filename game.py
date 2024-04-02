""" main client program to launch """

import api
from joueur import naif as p
import time

against_human = False

player1, token1 = api.create_player()
if not against_human:
    player2, token2 = api.create_player()


def main():
    """ 
    function to get the player who need to play, plays its turn and ends it
    """

    t = time.time()
    while not api.get_data(player1, token1):
        if time.time() - t > 10:
            print("!!! TIMEOUT !!!")
            exit(1)
    if api.current_player() == player1:
        p.nexturn(player1, token1)
        api.end_turn(player1, token1)
    elif not against_human:
        api.get_data(player2, token2)
        p.nexturn(player2, token2)
        api.end_turn(player2, token2)


if __name__ == "__main__":
    while True:
        main()
        # time.sleep(0.5)
