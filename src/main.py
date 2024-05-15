""" principale programme client à lancer pour jouer automatiquement """

import sys
import time
from apis import connection
from apis.players import Player


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


player1 = Player()
if TWO_PLAYERS:
    player2 = Player()


def main():
    """ 
    fonction pour connaitre le joueur dont c'est le tour, le faire jouer et finir son tour
    """

    time.sleep(0.1)  # avoid spamming the server
    t = time.time()
    while not connection.get_data(player1):
        if time.time() - t > 10:
            print("!!! TIMEOUT !!!")
            sys.exit(1)
    if connection.current_player() == player1:
        player1.nexturn()
        player1.end_turn()
    elif TWO_PLAYERS:
        connection.get_data(player2)
        player2.nexturn()
        player2.end_turn()


if __name__ == "__main__":
    while True:
        main()
        # time.sleep(0.5)
