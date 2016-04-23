import json
from os import path

from facet.settings import FACET_DIR


_FILE = path.join(FACET_DIR, ".state")


def read(key=None):
    try:
        with open(_FILE) as fp:
            state = json.load(fp)
    except FileNotFoundError:
        if key:
            raise
        else:
            state = {}
    return state[key] if key else state


def write(**kwargs):
    state = read()
    state.update(kwargs)
    with open(_FILE, 'w') as fp:
        return json.dump(state, fp, indent=2, sort_keys=True)
