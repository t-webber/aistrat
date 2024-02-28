import api
import random

kinds = api.getKinds()
print(kinds)
for (i,j) in kinds[api.PAWN]:
    vert = random.choice([True, False])
    move = random.choice([1, -1])
    if vert:
        api.move(api.PAWN, i,j,i, j+move)
    else:
        api.move(api.PAWN, i,j,i+move, j)
