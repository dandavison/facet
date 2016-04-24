import os
import subprocess
import sys
import webbrowser

import json

from facet import settings
from facet.cli_dispatch import Dispatcher
from facet.facet import Facet


class Command:
    """
    Switch contexts.

    Usage:
      facet [options] [COMMAND] [ARGS...]
      facet -h|--help

    Options:
      -v, --version      Print version and exit

    Commands:
      cd-facet           cd to facet directory
      cd-repo            cd to facet repo
      create             Create a facet for a JIRA issue
      current            Display facet
      edit               Edit facet
      fetch              Fetch JIRA data for facet
      fetch-all          Fetch JIRA data for all facets
      ls                 List facets
      summary            Display issue summary
      summary-all        Display all issue summaries
      workon             Switch to a facet
    """

    def cd_facet(self, options):
        """
        cd to facet directory.

        Usage:
          cd-facet [FACET]
        """
        self._cd('directory', options)

    def cd_repo(self, options):
        """
        cd to facet git repo.

        Usage:
          cd-repo [FACET]
        """
        self._cd('repo', options)

    def _cd(self, directory_attr, options):
        facet = self._get_facet(options)
        os.chdir(getattr(facet, directory_attr))
        os.execl('/bin/bash', '/bin/bash')

    def checkout(self, options):
        """
        cd to facet repo and checkout facet branch.

        Usage:
          checkout [FACET]
        """
        facet = self._get_facet(options)
        os.chdir(facet.repo)
        subprocess.check_call(['git', 'checkout', facet.branch])
        os.execl('/bin/bash', '/bin/bash')

    def create(self, options):
        """
        Create a facet for a JIRA issue.

        Usage:
          create JIRA_ISSUE
        """
        facet = Facet(name=options['JIRA_ISSUE'])
        if facet.exists():
            raise ValueError("Facet already exists: '%s'" % facet.name)
        os.mkdir(facet.directory)
        facet.write_config({
            'name': self.name,
            'branch': self.name,
        })
        facet.fetch()
        print(facet.colored_by_state(facet.name))

    def current(self, options):
        """
        Display current facet.

        Usage:
          current
        """
        facet = Facet.get_current()
        print(facet.colored_by_state(facet.name))

    def edit(self, options):
        """
        Edit facet

        Usage:
          edit [FACET]
        """
        facet = self._get_facet(options)
        os.execl('/bin/bash',
                 '/bin/bash', '-c', '$EDITOR %s' % facet.directory)

    def fetch(self, options):
        """
        Fetch JIRA issue data.

        Usage:
          fetch
        """
        facet = self._get_facet()
        facet.fetch()
        print(facet.colored_by_state(facet.name))

    def fetch_all(self, options):
        """
        Fetch JIRA issue data for all facets.

        Usage:
          fetch
        """
        for facet in Facet.get_all():
            facet.fetch()
            print(facet.colored_by_state(facet.name))

    def ls(self, options):
        """
        List facets.

        Usage:
          ls
        """
        for facet in Facet.get_all():
            print(facet.colored_by_state(facet.name))

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
        webbrowser.open(facet.jira_url)

    def summary(self, options, facet=None):
        """
        Display issue summary.

        Usage:
          summary [FACET]
        """
        if not facet:
            facet = self._get_facet(options)
        print('%s %s' % (facet.colored_by_state(facet.name),
                         facet.jira_issue.summary))

    def summary_all(self, options):
        """
        Display all issue summaries.

        Usage:
          summary_all
        """
        for facet in Facet.get_all():
            self.summary(options, facet=facet)

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
    return os.path.join(settings.FACET_DIR, project, 'jira.json')


def get_version_info():
    file = os.path.join(os.path.dirname(__file__), 'version.txt')
    return open(file).read().strip()


def main():
    dispatcher = Dispatcher(
        Command(),
        {'options_first': True, 'version': get_version_info()})

    options, handler, command_options = dispatcher.parse(sys.argv[1:])

    handler(options)
