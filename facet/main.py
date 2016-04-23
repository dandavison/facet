import os
import sys

from facet.cli import Dispatcher


class Command(object):
    """
    Switch contexts.

    Usage:
      facet [options] [COMMAND] [ARGS...]
      facet -h|--help

    Options:
      -v, --version               Print version and exit

    Commands:
      ls                 List projects
      workon             Switch to a project
    """

    def ls(self):
        """
        List projects.

        Usage:
          ls
        """
        print('ls')

    def workon(self):
        """
        Switch to a project

        Usage:
          workon [PROJECT]
        """
        print('workon')


def get_version_info():
    file = os.path.join(os.path.dirname(__file__), 'version.txt')
    return open(file).read().strip()


def main():
    dispatcher = Dispatcher(
        Command(),
        {'options_first': True, 'version': get_version_info()})

    options, handler, command_options = dispatcher.parse(sys.argv[1:])

    handler()
