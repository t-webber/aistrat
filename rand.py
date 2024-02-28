import api
import random

kinds = api.getKinds()
print(kinds)
for (i,j) in kinds[api.PAWN]:
    # vert = random.choice([True, False])
    y,x = random.choice(api.getMoves(i,j))
    # if vert:
    api.move(api.PAWN, i,j,y, x)
    # else:
        # api.move(api.PAWN, i,j,i+move, j)
