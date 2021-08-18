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
    # "ABAAA": "j",	
    "ABAAB": "k",
    "ABABA": "l",	
    "ABABB": "m",
    "ABBAA": "n",	
    "ABBAB": "o",
    "ABBBA": "p",	
    "ABBBB": "q",
    "BAAAA": "r",	
    "BAAAB": "s",
    "BAABA": "t",	
    "BAABB": "u",
    # "BAABB": "v",
    "BABAA": "w",	
    "BABAB": "x",
    "BABBA": "y",
    "BABBB": "z"
}

coded_string = input(">>> ")
coded_sentence = coded_string.split()

sentence = []
for coded_word in coded_sentence:
    sentence.append("".join(ABC.get(coded_word[i : i + 5], "?") for i in range(0, len(coded_word), 5)))

sentence_string = " ".join(sentence)
print(sentence_string)
