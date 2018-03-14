import os
import shutil
import subprocess
import sys

import json

from facet import settings
from facet.cli_dispatch import Dispatcher
from facet.core import Facet
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
      config             Display facet config
      directory          Open editor on facet directory
      create             Create a facet for a JIRA issue
      current            Display current facet
      edit               Edit facet
      fetch              Fetch JIRA data for facet
      follow             Follow/unfollow a facet
      github             Open Github branch diff / PR page in a browser
      jira               Open JIRA issue page in a browser
      ls                 Display all facets
      migrate            Apply a patch to facet configs
      notes              Open notes file for facet
      pr                 Open draft PR description file for facet
      rm                 Delete facet
      show               Display facet
      workon             Switch to a facet, cd to repo and checkout branch
    """

    def cd(self, options):
        """
        cd to facet directory.

        Usage:
          cd [FACET]
        """
        facet = self._get_facet(options)
        self._cd(facet.directory)

    @staticmethod
    def _cd(directory):
        if append_to_prompt_commands_file('cd %s\n' % directory):
            sys.exit(0)
        else:
            os.chdir(directory)
            os_exec(['/bin/bash'])

    def config(self, options):
        """
        Display facet config

        Usage:
          config [FACET]
        """
        facet = self._get_facet(options)
        sys.stdout.write(open(facet.config_file).read())

    def directory(self, options):
        """
        Open editor on facet directory

        Usage:
          directory [FACET]
        """
        facet = self._get_facet(options)
        os_exec(['/bin/bash', '-c', '$EDITOR %s' % facet.directory])

    def notes(self, options):
        """
        Open facet notes file

        Usage:
          notes [FACET]
        """
        facet = self._get_facet(options)
        os_exec(['/bin/bash', '-c', '$EDITOR %s' % facet.notes_file])

    def pr(self, options):
        """
        Open facet PR.md file

        Usage:
          pr [FACET]
        """
        facet = self._get_facet(options)
        os_exec(['/bin/bash', '-c', '$EDITOR %s' % facet.pr_file])

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
        if options.get('FACET'):
            facets = [self._get_facet(options)]
        else:
            include_inactive = options.get('--all')
            facets = Facet.get_all(include_inactive)
        for facet in facets:
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
          -a, --all     Include done and non-followed facets
        """
        include_inactive = options.get('--all')
        for facet in Facet.get_all(include_inactive):
            print(facet.format())

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

    def jira(self, options):
        """
        Open JIRA issue page in a browser.

        Usage:
          jira [FACET]
        """
        facet = self._get_facet(options)
        url = facet.jira_url
        if not url:
            error('facet %s has no JIRA URL' % facet.name)
        open_url(url)

    def github(self, options):
        """
        Open Github branch diff / PR page in a browser.

        Usage:
          github [FACET]
        """
        facet = self._get_facet(options)
        url = facet.github_url
        if not url:
            error('facet %s has no Github URL' % facet.name)
        open_url(url)

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
        Switch facet, cd to repo and optionally checkout branch.

        Usage:
          workon [options] [FACET]

        Options:
          -c, --checkout     Also checkout facet's branch
        """
        facet = self._get_facet(options)
        Facet.set_current(facet)
        os.chdir(facet.repo)
        if options.get('--checkout') and facet.branch:
            self._checkout(facet.branch)
        self._cd(facet.repo)

    @staticmethod
    def _checkout(branch):
        try:
            subprocess.check_call(['git', 'checkout', branch])
        except subprocess.CalledProcessError as ex:
            warning("Branch %s does not exist; "
                    "creating it as branch off master" % branch)
            try:
                subprocess.check_call(
                    ['git', 'checkout', '-b', branch, 'master'],
                )
            except subprocess.CalledProcessError as ex:
                warning('{ex_cls}: {ex}'.format(
                    ex_cls=type(ex).__name__,
                    ex=ex,
                ))

    def _get_facet(self, options):
        name = options.get('FACET')
        if name:
            facet = Facet(name=name)
            if not facet.exists():
                error("No such facet: '%s'" % facet.name)
        else:
            facet = Facet.get_current()
        return facet


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
