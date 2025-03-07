""" principale programme client à lancer pour jouer automatiquement """

import sys
import time
from apis import connection
from player import next_turn as p
from apis.player import Player


if len(sys.argv) > 2 and sys.argv[2]:
    connection.init(sys.argv[2])
else:
    connection.init("http://localhost:8080")

print("IP = ", connection.IP)

if len(sys.argv) > 1:
    TWO_PLAYERS = sys.argv[1] == '2'
else:
    TWO_PLAYERS = False

print(sys.argv)
print("TWO_PLAYERS ? = ", TWO_PLAYERS)


player1, token1 = connection.create_player()
if TWO_PLAYERS:
    player2, token2 = connection.create_player()


def main():
    """ 
    fonction pour connaitre le joueur dont c'est le tour, le faire jouer et finir son tour
    """

    time.sleep(0.1)  # avoid spamming the server
    t = time.time()
    while not connection.get_data(player1, token1):
        if time.time() - t > 10:
            print("!!! TIMEOUT !!!")
            sys.exit(1)
    if connection.current_player() == player1:
        p.nexturn(player1, token1)
        connection.end_turn(player1,token1)
    elif TWO_PLAYERS:
        connection.get_data(player2,token2)
        p.nexturn(player2, token2)
        connection.end_turn(player2,token2)


if __name__ == "__main__":
    while True:
        main()
        # time.sleep(0.5)
