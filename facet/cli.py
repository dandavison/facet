import os
import shutil
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
from facet.utils import error
from facet.utils import os_exec
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
      configure          Configure facet
      create             Create a facet for a JIRA issue
      current            Display current facet
      edit               Edit facet
      fetch              Fetch JIRA data for facet
      follow             Follow/unfollow a facet
      ls                 Display all facets
      migrate            Apply a patch to facet configs
      rm                 Delete facet
      show               Display facet
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
            os_exec(['/bin/bash'])

    def checkout(self, options):
        """
        cd to facet repo and checkout facet branch.

        Usage:
          checkout [FACET]
        """
        self.workon(options)
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

    def configure(self, options):
        """
        Configure facet

        Usage:
          configure [FACET]
        """
        facet = self._get_facet(options)
        os_exec(['/bin/bash', '-c', '$EDITOR %s' % facet.directory])

    def create(self, options):
        """
        Create a facet for a JIRA issue.

        Usage:
          create [options] NAME

        Options:
          -j, --jira  Create a JIRA facet.
        """
        facet = Facet(name=options['NAME'])
        if facet.exists():
            raise ValueError("Facet already exists: '%s'" % facet.name)

        jira_issue = (prompt_for_user_input('JIRA issue', facet.name)
                      if options.get('--jira') else None)
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
        try:
            facet.fetch()
        except IOError as ex:
            warning('%s: %s' % (type(ex).__name__, ex))

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
        os_exec(['/bin/bash', '-c', '$EDITOR %s' % facet.repo])

    def fetch(self, options):
        """
        Fetch JIRA issue data for facet.

        Usage:
          fetch [options]

        Options:
          -a, --all     Fetch all facets
        """
        for facet in self._get_facets(options):
            facet.fetch()
            print(facet.format())

    def follow(self, options):
        """
        Follow facet.

        Usage:
          follow [options] [FACET]

        Options:
          -n, --unfollow    Unfollow facet
        """
        facet = self._get_facet(options)
        if options.get('--unfollow'):
            facet.unfollow()
        else:
            facet.follow()

    def ls(self, options):
        """
        List facets.

        Usage:
          ls [options]

        Options:
          -a, --all     Include non-followed facets
        """
        for facet in Facet.get_all():
            if options.get('--all') or (
                    facet.following and not facet.is_done):
                self.show(options, facet=facet)

    def migrate(self, options, facet=None):
        """
        Migrate facet.

        Usage:
          migrate [options] [FACET] PATCH

        Options:
          -a, --all     Migrate all facets
        """
        if not facet:
            facet = self._get_facet(options)
        patch = json.loads(options['PATCH'])
        facet.apply_patch(patch)

    def open_jira(self, options):
        """
        Open JIRA issue

        Usage:
          open-jira [FACET]
        """
        facet = self._get_facet(options)
        open_url(facet.jira_url)

    def rm(self, options):
        """
        Delete facet.

        Usage:
          rm [FACET]
        """
        facet = self._get_facet(options)
        ok = prompt_for_user_input("OK to delete facet '%s'?" % facet.name,
                                   True)
        if ok:
            shutil.rmtree(facet.directory)

    def show(self, options, facet=None):
        """
        Display facet.

        Usage:
          show [FACET]
        """
        if not facet:
            facet = self._get_facet(options)
        print(facet.format())

    def workon(self, options):
        """
        Switch to a project

        Usage:
          workon FACET
        """
        Facet.set_current(self._get_facet(options))

    def _get_facet(self, options):
        name = options.get('FACET')
        if name:
            facet = Facet(name=name)
            if not facet.exists():
                error("No such facet: '%s'" % facet.name)
        else:
            facet = Facet.get_current()
        return facet

    def _get_facets(self, options):
        if options.get('--all'):
            return Facet.get_all()
        else:
            return [self._get_facet(options)]


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

    try:
        handler(options)
    except KeyboardInterrupt:
        sys.exit(1)
