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

coded_string = input(">>> ")
coded_sentence = coded_string.split()

sentence = []
for coded_word in coded_sentence:
    sentence.append("".join(ABC.get(coded_word[i : i + 5], "?") for i in range(0, len(coded_word), 5)))

sentence_string = " ".join(sentence)
print(sentence_string)
