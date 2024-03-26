""" main client program to launch """

import api
# from joueur import rand
from joueur import naif as p
import time

player1, token1 = api.create_player()
player2, token2 = api.create_player()


def main():
    """ 
    function to get the player who need to play, plays its turn and ends it
    """

    api.get_data(player1, token1)
    if api.current_player() == player1:
        p.nexturn(player1, token1)
        api.end_turn(player1, token1)
    else:
        api.get_data(player2, token2)
        p.nexturn(player2, token2)
        api.end_turn(player2, token2)


if __name__ == "__main__":
    t = time.time()
    while True:
        main()
        if time.time() - t > 15:
            print("! TIMEOUT !")
            break
        # time.sleep(0.5)
