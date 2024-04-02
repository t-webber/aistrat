""" main client program to launch """

import sys
import time
from joueur import naif as p
import api

if len(sys.argv) > 1:
    api.init(sys.argv[1])
else:
    api.init("http://localhost:8080")

print("IP = ", api.IP)


player1, token1 = api.create_player()


def main():
    """ 
    function to wait for my turn
    """

    t = time.time()
    while not api.get_data(player1, token1):
        if time.time() - t > 10:
            sys.exit(1)

    if api.current_player() == player1:
        p.nexturn(player1, token1)
        api.end_turn(player1, token1)


if __name__ == "__main__":
    while True:
        main()
