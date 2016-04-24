from os import path

import yaml


FACET_DIR = path.expanduser("~/.facet")
FACETS_DIR = path.join(FACET_DIR, 'facets')
JIRA_AUTH_FILE = path.join(FACET_DIR, '.auth.yaml')
LOCAL_SETTINGS_FILE = path.join(FACET_DIR, 'settings.yaml')

# Set these in LOCAL_SETTINGS_FILE
JIRA_HOST = None
DEFAULT_REPO = None

# Import local settings
if path.exists(LOCAL_SETTINGS_FILE):
    with open(LOCAL_SETTINGS_FILE) as fp:
        locals().update(yaml.load(fp))

if DEFAULT_REPO:
    DEFAULT_REPO = path.expanduser(DEFAULT_REPO)
