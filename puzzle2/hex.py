def hex(in_string):
    in_object = bytes.fromhex(in_string)
    out_string = in_object.decode("ASCII")
    return out_string
