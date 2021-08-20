from csv import writer
from json import load

deciphered = load(open("deciphered.json", "r"))
spreadsheet = writer(open("spreadsheet.csv", "w", newline=""), delimiter=",")

for in_string, out_string in deciphered.items():
    print(in_string)
    print(out_string)
    effect = int(input(">>> "))
    spreadsheet.writerow([in_string, out_string, effect])
    print()
