import os
import subprocess
import sys

import json

from facet import settings
from facet.cli_dispatch import Dispatcher
from facet.facet import Facet
from facet.webbrowser import open_url
from facet.utils import append_to_prompt_commands_file
from facet.utils import delete_prompt_commands_file
from facet.utils import prompt_for_user_input
from facet.utils import warning


class Command:
    """
    Switch contexts.

    Usage:
      facet [options] [COMMAND] [ARGS...]
      facet -h|--help

    Options:
      -v, --version      Print version and exit

    Commands:
      cd                 cd to facet directory
      checkout           cd to facet repo and checkout facet branch
      config             Display facet config
      create             Create a facet for a JIRA issue
      current            Display current facet
      edit               Edit facet
      fetch              Fetch JIRA data for facet
      fetch-all          Fetch JIRA data for all facets
      ls                 Display all facets
      show               Display facet
      unfollow           Unfollow facet
      workon             Switch to a facet
    """

    def cd(self, options):
        """
        cd to facet directory.

        Usage:
          cd [FACET]
        """
        facet = self._get_facet(options)
        self._cd(facet.directory)

    def _cd(self, directory):
        if append_to_prompt_commands_file('cd %s\n' % directory):
            sys.exit(0)
        else:
            os.chdir(directory)
            os.execv('/bin/bash', ('/bin/bash',))

    def checkout(self, options):
        """
        cd to facet repo and checkout facet branch.

        Usage:
          checkout [FACET]
        """
        facet = self._get_facet(options)
        os.chdir(facet.repo)
        try:
            subprocess.check_call(['git', 'checkout', facet.branch])
        except subprocess.CalledProcessError as ex:
            warning('{ex_cls}: {ex}'.format(
                ex_cls=type(ex).__name__,
                ex=ex,
            ))
        self._cd(facet.repo)

    def config(self, options):
        """
        Display facet config

        Usage:
          config [FACET]
        """
        facet = self._get_facet(options)
        sys.stdout.write(open(facet.config_file).read())

    def create(self, options):
        """
        Create a facet for a JIRA issue.

        Usage:
          create NAME
        """
        facet = Facet(name=options['NAME'])
        if facet.exists():
            raise ValueError("Facet already exists: '%s'" % facet.name)

        jira_issue = prompt_for_user_input('JIRA issue', facet.name)
        repo = prompt_for_user_input('Git repo', settings.DEFAULT_REPO)
        branch = prompt_for_user_input('Branch', facet.name)

        config = {
            key: val
            for key, val in [('name', facet.name),
                             ('repo', repo),
                             ('branch', branch),
                             ('jira', jira_issue)]
            if val
        }
        config['follow'] = True

        os.mkdir(facet.directory)
        facet.write_config(config)
        facet.fetch()
        print(facet.style(facet.name))

    def current(self, options):
        """
        Display current facet.

        Usage:
          current
        """
        facet = Facet.get_current()
        print(facet.format())

    def edit(self, options):
        """
        Edit facet

        Usage:
          edit [FACET]
        """
        facet = self._get_facet(options)
        os.execv('/bin/bash',
                 ('/bin/bash', '-c', '$EDITOR %s' % facet.directory))

    def fetch(self, options):
        """
        Fetch JIRA issue data.

        Usage:
          fetch
        """
        facet = self._get_facet(options)
        facet.fetch()
        print(facet.style(facet.name))

    def fetch_all(self, options):
        """
        Fetch JIRA issue data for all facets.

        Usage:
          fetch
        """
        for facet in Facet.get_all():
            facet.fetch()
            print(facet.style(facet.name))

        for facet in Facet.get_all():
            print(facet.style(facet.name))

    def follow(self, options):
        """
        Follow facet.

        Usage:
          follow [FACET]
        """
        facet = self._get_facet(options)
        facet.follow()

    def ls(self, options):
        """
        List facets.

        Usage:
          ls
        """
        for facet in Facet.get_all():
            if facet.following and not facet.is_done:
                self.show(options, facet=facet)

    def migrate(self, options, facet=None):
        """
        Migrate facet.

        Usage:
          migrate FACET PATCH
        """
        if not facet:
            facet = self._get_facet(options)
        patch = json.loads(options['PATCH'])
        facet.apply_patch(patch)

    def migrate_all(self, options):
        """
        Migrate all facets.

        Usage:
          migrate_all PATCH
        """
        for facet in Facet.get_all():
            self.migrate(options, facet=facet)

    def open_jira(self, options):
        """
        Open JIRA issue

        Usage:
          open-jira [FACET]
        """
        facet = self._get_facet(options)
        open_url(facet.jira_url)

    def show(self, options, facet=None):
        """
        Display facet.

        Usage:
          show [FACET]
        """
        if not facet:
            facet = self._get_facet(options)
        print(facet.format())

    def unfollow(self, options):
        """
        Unfollow facet.

        Usage:
          unfollow [FACET]
        """
        facet = self._get_facet(options)
        facet.unfollow()

    def workon(self, options):
        """
        Switch to a project

        Usage:
          workon FACET
        """
        facet = Facet(name=options['FACET'])
        Facet.set_current(facet)

    def _get_facet(self, options):
        name = options.get('FACET')
        return Facet(name=name) if name else Facet.get_current()


def jira_data_file(project):
    return os.path.join(settings.FACETS_DIR, project, 'jira.json')


def get_version_info():
    file = os.path.join(os.path.dirname(__file__), 'version.txt')
    return open(file).read().strip()


def main():
    delete_prompt_commands_file()
    dispatcher = Dispatcher(
        Command(),
        {'options_first': True, 'version': get_version_info()})

    options, handler, command_options = dispatcher.parse(sys.argv[1:])

    handler(options)
