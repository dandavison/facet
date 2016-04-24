# -*- coding: utf-8 -*-
import json
from os import listdir
from os import path

import requests

from facet import settings
from facet import state
from facet.jira import JiraIssue
from facet.utils import dump_json
from facet.utils import dump_yaml
from facet.utils import get_auth


_FACET_CONFIG_FILE_NAME = 'facet.yaml'
_JIRA_DATA_FILE_NAME = 'jira.json'


class Facet:
    def __init__(self, name):
        self.name = name

    @classmethod
    def get_current(cls):
        return cls(name=state.read('facet'))

    @staticmethod
    def set_current(facet):
        state.write(facet=facet.name)

    @classmethod
    def get_all(cls):
        for name in cls.get_all_names():
            yield cls(name=name)

    @staticmethod
    def get_all_names():
        for name in sorted(listdir(settings.FACET_DIR)):
            if not name.startswith('.'):
                yield name

    def exists(self):
        return self.name in self.get_all_names()

    def write_initial_facet_config(self):
        config = {
            'name': self.name,
            'branch': self.name,
        }
        with open(self.facet_config_file, 'w') as fp:
            dump_yaml(config, fp)

    def fetch(self):
        with open(self.jira_data_file, 'w') as fp:
            dump_json(requests.get(self.jira_json_url).json(), fp)

    @property
    def jira_json_url(self):
        return ("https://{username}:{password}@{host}"
                "/rest/api/latest/issue/{issue}".format(
                    host=settings.JIRA_HOST,
                    issue=self.name,
                    **get_auth()
                ))

    @property
    def directory(self):
        return path.join(settings.FACET_DIR, self.name)

    @property
    def facet_config_file(self):
        return path.join(self.directory, _FACET_CONFIG_FILE_NAME)

    @property
    def jira_data_file(self):
        return path.join(self.directory, _JIRA_DATA_FILE_NAME)

    @property
    def jira_issue(self):
        if not path.exists(self.jira_data_file):
            self.fetch()
        with open(self.jira_data_file) as fp:
            return JiraIssue(json.load(fp))

    def colored_by_state(self, string):
        return self.jira_issue.colored_by_state(string)
