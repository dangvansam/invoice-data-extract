import json

def binary2json(b_string):
    u_string = b_string.decode('utf-8').replace("'", '"')
    json_obj = json.loads(u_string)
    return json_obj