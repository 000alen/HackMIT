from csv import writer
from json import load

out_puzzle2 = load(open("out_puzzle2.json", "r"))
out_effects = writer(open("out_effects.csv", "w", newline=""), delimiter=",")

for in_string, out_string in out_puzzle2.items():
    print(in_string)
    print(out_string)
    effect = int(input(">>> "))
    out_effects.writerow([in_string, out_string, effect])
    print()
