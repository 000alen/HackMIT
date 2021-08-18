ABC = {
    "AAAAA": "a",
    "AAAAB": "b",
    "AAABA": "c",
    "AAABB": "d",
    "AABAA": "e",
    "AABAB": "f",
    "AABBA": "g",
    "AABBB": "h",
    "ABAAA": "i",
    "ABAAB": "j",
    "ABABA": "k",
    "ABABB": "l",
    "ABBAA": "m",
    "ABBAB": "n",
    "ABBBA": "o",
    "ABBBB": "p",
    "BAAAA": "q",
    "BAAAB": "r",
    "BAABA": "s",
    "BAABB": "t",
    "BABAA": "u",
    "BABAB": "v",
    "BABBA": "w",
    "BABBB": "x",
    "BBAAA": "y",
    "BBAAB": "z"
}

def bacon(in_string):
    in_sentence = in_string.split()

    out_sentence = []
    for in_word in in_sentence:
        out_sentence.append("".join(ABC.get(in_word[i : i + 5], "?") for i in range(0, len(in_word), 5)))

    out_string = " ".join(out_sentence)
    return out_string
