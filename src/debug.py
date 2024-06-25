import sys

def log_func(name: str):
    if len(sys.argv) > 2 and sys.argv[2] == "debug":
        print(f"DEBUT de {name}")

def log_func_destination(i: int,j: int):
    if len(sys.argv) > 2 and sys.argv[2] == "debug":
        print(f"destination is {i,j}")

def pause(id: str):
    if id =='A' and len(sys.argv) > 2 and sys.argv[2] == "debug":
        input("Press Enter to continue...")