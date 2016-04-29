import json
from os import path

from facet import settings
from facet.utils import dump_json


_FILE = path.join(settings.FACET_DIR, "state.json")


def read(key=None):
    try:
        with open(_FILE) as fp:
            state = json.load(fp)
    except FileNotFoundError:
        if key:
            raise
        else:
            state = {}
    return state.get(key) if key is not None else state


def write(**kwargs):
    state = read()
    state.update(kwargs)
    with open(_FILE, 'w') as fp:
        return dump_json(state, fp)
