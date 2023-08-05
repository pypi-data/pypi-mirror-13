import json


def read_local_storage(filename='local_storage.json'):
    with open(filename) as inf:
        return json.load(inf)

def write_local_storage(data, filename='local_storage.json'):
    with open(filename, 'w') as outf:
        json.dump(data, outf)
