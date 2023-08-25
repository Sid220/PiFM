import json


def get_conf():
    with open('conf.json') as f:
        data = json.load(f)
    return data
