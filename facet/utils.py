import getpass
import json

import yaml

from facet import settings


def dump_json(obj, fp):
    json.dump(obj, fp, indent=2, sort_keys=True)


def dump_yaml(obj, fp):
    yaml.dump(obj, fp, indent=2, default_flow_style=False)


class memoized:

    def __init__(self, fn):
        self.fn = fn
        self.cache = {}

    def __call__(self, *args, **kwargs):
        key = self.make_key(*args, **kwargs)
        if key not in self.cache:
            self.cache[key] = self.fn(*args, **kwargs)
        return self.cache[key]

    @staticmethod
    def make_key(*args, **kwargs):
        return json.dumps([args, kwargs], sort_keys=True)


@memoized
def get_auth():
    try:
        with open(settings.JIRA_AUTH_FILE) as fp:
            auth = yaml.load(fp)
    except FileNotFoundError:
        print("Auth credentials can be stored in {file}. "
              "Keys are 'username' and 'password'. Both optional.".format(
                  file=settings.JIRA_AUTH_FILE))
        auth = {}

    assert not auth.keys() - {'username', 'password'}, \
        "auth.yaml keys should be 'username' and 'password' (both optional)"

    if 'username' not in auth:
        auth['username'] = input("JIRA username: "),
    if 'password' not in auth:
        auth['password'] = getpass.getpass("JIRA password: ")

    return auth
