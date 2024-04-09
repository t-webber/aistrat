""" main client program to launch for auto playing """

import sys
import time
import api
from joueur import naif as p


if len(sys.argv) > 1:
    api.init(sys.argv[1])
else:
    api.init("http://localhost:8080")

print("IP = ", api.IP)

player1, token1 = api.create_player()
if len(sys.argv) > 2:
    player2, token2 = api.create_player()
    TWO_PLAYERS = True
else:
    TWO_PLAYERS = False


def main():
    """ 
    function to get the player who need to play, plays its turn and ends it
    """

    t = time.time()
    while not api.get_data(player1, token1):
        if time.time() - t > 10:
            print("!!! TIMEOUT !!!")
            sys.exit(1)
    if api.current_player() == player1:
        p.nexturn(player1, token1)
        api.end_turn(player1, token1)
    elif TWO_PLAYERS:
        api.get_data(player2, token2)
        p.nexturn(player2, token2)
        api.end_turn(player2, token2)


if __name__ == "__main__":
    while True:
        main()
        # time.sleep(0.5)
