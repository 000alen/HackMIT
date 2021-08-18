hex_string = input(">>> ")
bytes_object = bytes.fromhex(hex_string)
string = bytes_object.decode("ASCII")

print(string)