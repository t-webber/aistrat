"""Programme principal client à lancer pour jouer automatiquement."""

import sys
import time
from apis import connection
from apis.players.players import Player


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
    """Fonction pour connaitre le joueur dont c'est le tour, le faire jouer et finir son tour."""
    time.sleep(0.1)  # avoid spamming the server
    t = time.time()
    while not connection.get_data(player1.id, player1.token):
        if time.time() - t > 10:
            print("!!! TIMEOUT !!!")
            sys.exit(1)
    if connection.current_player() == player1:
        player1.next_turn()
    elif TWO_PLAYERS:
        player2.next_turn()


if __name__ == "__main__":

    while True:
        main()
        # time.sleep(0.5)
