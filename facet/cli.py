import os
import sys

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
      current            Display current facet
      fetch              Fetch JIRA data for current facet
      fetch-all          Fetch JIRA data for all facets
      ls                 List facets
      summary            Display issue summary
      summary-all        Display all issue summaries
      workon             Switch to a facet
    """

    def cd(self, options):
        """
        Change to facet directory.

        Usage:
          cd
        """
        directory = self._get_facet(options).directory
        os.chdir(directory)
        os.execl('/bin/bash', '/bin/bash')

    def current(self, options):
        """
        Display current facet.

        Usage:
          current
        """
        print(Facet.get_current())

    def fetch(self, options):
        """
        Fetch JIRA issue data.

        Usage:
          fetch
        """
        facet = self._get_facet()
        facet.fetch()
        print(facet)

    def fetch_all(self, options):
        """
        Fetch JIRA issue data for all facets.

        Usage:
          fetch
        """
        for facet in Facet.get_all():
            facet.fetch()
            print(facet)

    def ls(self, options):
        """
        List facets.

        Usage:
          ls
        """
        for name in Facet.get_all_names():
            print(name)

    def summary(self, options, facet=None):
        """
        Display issue summary.

        Usage:
          summary [FACET]
        """
        if not facet:
            facet = self._get_facet(options)
        print('%s %s' % (facet.colored(facet.name), facet.jira_issue.summary))

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
