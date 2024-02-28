import api
import random

ME = api.createPlayer()

while True: 
    if api.getPlayer() != ME: continue

    print("Turn of", ME)

    api.getData()
    kinds = api.getKinds()
    print(kinds)
    for (i,j) in kinds[api.PAWN]:
        # vert = random.choice([True, False])
        y,x = random.choice(api.getMoves(i,j))
        # if vert:
        api.move(api.PAWN,i,j,y,x)
        # else:
            # api.move(api.PAWN, i,j,i+move, j)


    api.endTurn()
