import getpass
import json
import os
import sys

import yaml
from clint.textui.colored import colorama

from facet import settings


def dump_json(obj, fp):
    json.dump(obj, fp, indent=2, sort_keys=True)


def dump_yaml(obj, fp):
    yaml.dump(obj, fp, indent=2, default_flow_style=False)


def prompt_for_user_input(prompt, default=None):
    prompt = '{prompt} [{default}]: '.format(prompt=prompt, default=default)
    return input(prompt) or default


def append_to_prompt_commands_file(text):
    if settings.PROMPT_COMMANDS_FILE:
        with open(settings.PROMPT_COMMANDS_FILE, 'a') as fp:
            fp.write(text)
        return True
    return False


def delete_prompt_commands_file():
    prompt_commands_file = settings.PROMPT_COMMANDS_FILE
    if prompt_commands_file and os.path.exists(prompt_commands_file):
        os.remove(prompt_commands_file)


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


def default_color(s, always=False, bold=False):
    if bold and (always or sys.stdout.isatty()):
        return '{on}{string}{off}'.format(
            on=getattr(colorama.Style, 'BRIGHT'),
            string=s,
            off=getattr(colorama.Style, 'NORMAL'))
    else:
        return s
