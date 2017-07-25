from os import environ
from os import getenv
from os import path

import yaml


FACET_DIR = path.expanduser(environ.get('FACET_DIRECTORY', '~/.facet'))
FACETS_DIR = path.join(FACET_DIR, 'facets')
JIRA_AUTH_FILE = path.join(FACET_DIR, 'auth.yaml')
LOCAL_SETTINGS_FILE = path.join(FACET_DIR, 'settings.yaml')

NOTES_FILE_NAME = 'notes.txt'

# Set these in LOCAL_SETTINGS_FILE
JIRA_HOST = None
DEFAULT_REPO = None

# Path to a file that facet can write shell commands to and delete. If setting
# this, you must arrange for your shell to source the file when generating its
# prompt, i.e. in $PROMPT_COMMAND in bash
PROMPT_COMMANDS_FILE = None

# Import local settings
if path.exists(LOCAL_SETTINGS_FILE):
    with open(LOCAL_SETTINGS_FILE) as fp:
        locals().update(yaml.load(fp))

for path_var in [
        'DEFAULT_REPO',
        'PROMPT_COMMANDS_FILE',
]:
    path_val = locals()[path_var]
    if path_val:
        locals()[path_var] = path.expanduser(path_val)

if locals()['DEFAULT_REPO'].endswith('website') and getenv('WEBSITE'):
    locals()['DEFAULT_REPO'] += '-' + getenv('WEBSITE')
