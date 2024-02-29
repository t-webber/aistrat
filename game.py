import api
from joueur import rand
from joueur import naif as p

player1,token1 = api.createPlayer()
player2,token2 = api.createPlayer()

while True:
    api.getData(player1,token1)
    if api.currentPlayer() == player1:
        p.nexturn(player1, token1)
        api.endTurn(player1,token1)
    else :
        api.getData(player2, token2)
        p.nexturn(player2, token2)
        api.endTurn(player2,token2)
