from json import load, dump
from bacon import bacon
from hex import hex 
from beaufort import beaufort

puzzle2 = load(open("puzzle2.json"))

out_puzzle2 = {}
for method, string in puzzle2:
    if method == "bacon":
        out_puzzle2[string] = bacon(string)
    elif method == "hex":
        out_puzzle2[string] = hex(string)
    elif method == "beaufort":
        out_puzzle2[string] = beaufort(string)
    else:
        raise Exception("You made a typo")

dump(out_puzzle2, open("out_puzzle2.json", "w"))
