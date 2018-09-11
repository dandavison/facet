# -*- coding: utf-8 -*-
import asyncio
import json
import subprocess
from os import listdir
from os import path

import aiohttp
import requests
import yaml

from facet import settings
from facet import state
from facet.jira import JiraIssue
from facet.utils import default_color
from facet.utils import dump_json
from facet.utils import dump_yaml
from facet.utils import get_auth


_CONFIG_FILE_NAME = 'facet.yaml'
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
        subprocess.check_call([
            'touch',
            path.join(settings.FACETS_DIR, facet.name),
        ])

    @classmethod
    def get_all(cls, include_inactive=False):
        for name in cls.get_all_names():
            facet = cls(name=name)
            if facet.is_active or include_inactive:
                yield facet

    @staticmethod
    def get_all_names():
        file_names = [
            name.decode('utf-8')
            for name in (subprocess
                         .check_output(['ls', '-1', '-t', settings.FACETS_DIR])
                         .splitlines())
        ]
        for name in file_names:
            if not name.startswith('.'):
                yield name

    def exists(self):
        return self.name in self.get_all_names()

    def read_config(self, key=None):
        with open(self.config_file) as fp:
            config = yaml.load(fp)
        return config.get(key) if key is not None else config

    def write_config(self, config=None, **kwargs):
        if config is None:
            config = self.read_config()
            config.update(kwargs)
        with open(self.config_file, 'w') as fp:
            dump_yaml(config, fp)

    def apply_patch(self, patch):
        # TODO: deep dicts
        config = patch.copy()
        config.update(self.read_config())
        self.write_config(config)

    def fetch(self):
        async def _fetch():
            conn = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=conn) as session:
                await self._fetch_async(session)

        event_loop = asyncio.new_event_loop()
        try:
            event_loop.run_until_complete(_fetch())
        finally:
            event_loop.close()

    async def _fetch_async(self, session):
        if not self.jira:
            return
        resp = await session.get(self.jira_json_url)
        resp.raise_for_status()
        _json = await resp.json()
        assert _json
        with open(self.jira_data_file, 'w') as fp:
            dump_json(_json, fp)
        print(self.format())

    def format(self):
        if self.jira:
            try:
                jira_issue = self.get_jira_issue()
            except IOError as ex:
                summary = '<failed to fetch summary>'
            else:
                summary=self.style(jira_issue.summary, color=False)
            return '{name} {summary}'.format(
                name=self.style(self.name),
                summary=summary,
            )
        else:
            return self.style(self.name)

    @property
    def github_url(self):
        if not settings.GITHUB_REPO_URL:
            return None
        return ('{github_repo_url}/pull/{branch}'.format(
            github_repo_url=settings.GITHUB_REPO_URL,
            branch=self.branch,
        ))

    @property
    def jira_url(self):
        return ("https://{host}"
                "/browse/{issue}".format(
                    host=settings.JIRA_HOST,
                    issue=self.name,
                ))

    @property
    def jira_json_url(self):
        return ("https://{username}:{password}@{host}"
                "/rest/api/latest/issue/{issue}".format(
                    host=settings.JIRA_HOST,
                    issue=self.jira,
                    **get_auth()
                ))

    @property
    def url(self):
        # TODO: non-JIRA URLs
        return self.jira_url

    @property
    def directory(self):
        return path.join(settings.FACETS_DIR, self.name)

    @property
    def notes_file(self):
        for file_name in [settings.NOTES_FILE_NAME, 'notes.md', 'notes.org', 'notes.py']:
            file_path = path.join(self.directory, file_name)
            if path.exists(file_path):
                return file_path
        return path.join(self.directory, settings.NOTES_FILE_NAME)

    @property
    def pr_file(self):
        return path.join(self.directory, 'PR.md')

    @property
    def config_file(self):
        return path.join(self.directory, _CONFIG_FILE_NAME)

    @property
    def jira_data_file(self):
        return path.join(self.directory, _JIRA_DATA_FILE_NAME)

    @property
    def is_active(self):
        return self.read_config('follow') and not self.is_done

    def follow(self):
        self.write_config(follow=True)

    def unfollow(self):
        self.write_config(follow=False)

    @property
    def jira(self):
        return self.read_config('jira')

    def get_jira_issue(self):
        if not path.exists(self.jira_data_file):
            self.fetch()
        with open(self.jira_data_file) as fp:
            _json = fp.read()
            assert _json, f'{self.jira_data_file} is empty'
            return JiraIssue(json.loads(_json))

    @property
    def branch(self):
        return self.read_config('branch')

    @property
    def repo(self):
        return path.expanduser(self.read_config('repo'))

    @property
    def is_done(self):
        if self.jira:
            return self.get_jira_issue().is_done
        else:
            return None

    def style(self, string, color=True):
        is_current = self == self.get_current()
        if not color or not self.jira:
            style_function = default_color
        else:
            try:
                jira_issue = self.get_jira_issue()
            except IOError:
                style_function = default_color
            else:
                style_function = jira_issue.get_style_function()

        return style_function(string, bold=is_current, always=True)

    def __eq__(self, other):
        return self.name == other.name
