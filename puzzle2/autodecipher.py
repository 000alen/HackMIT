from json import load, dump
from decipher.bacon import bacon
from decipher.hex import hex 
from decipher.beaufort import beaufort

# {[cipher, message], ...}
ciphered = load(open("ciphered.json"))

deciphered = {}
for method, string in ciphered:
    if method == "bacon":
        deciphered[string] = bacon(string)
    elif method == "hex":
        deciphered[string] = hex(string)
    elif method == "beaufort":
        deciphered[string] = beaufort(string)
    else:
        raise Exception("You made a typo")

dump(deciphered, open("deciphered.json", "w"))
