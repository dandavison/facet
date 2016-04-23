from os import listdir
from os import path

import requests

from facet import settings
from facet import state
from facet.utils import dump_json
from facet.utils import get_auth


_JIRA_DATA_FILE_NAME = 'jira.json'


class Facet:
    def __init__(self, name):
        self.name = name

    @classmethod
    def get_current(cls):
        return cls(name=state.read('facet'))

    @classmethod
    def get_all(cls):
        for name in cls.get_all_names():
            yield cls(name=name)

    @staticmethod
    def get_all_names():
        for name in sorted(listdir(settings.FACET_DIR)):
            if not name.startswith('.'):
                yield name

    def fetch(self):
        with open(self.jira_data_file, 'w') as fp:
            dump_json(requests.get(self.jira_url).json(), fp)

    @property
    def jira_url(self):
        return ("https://{username}:{password}@jira.counsyl.com"
                "/rest/api/latest/issue/{issue}".format(
                    issue=self.name,
                    **get_auth()
                ))

    @property
    def directory(self):
        return path.join(settings.FACET_DIR, self.name)

    @property
    def jira_data_file(self):
        return path.join(self.directory, _JIRA_DATA_FILE_NAME)
