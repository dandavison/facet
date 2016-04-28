import re
import subprocess
import webbrowser


class ChromeCli:
    TAB_REGEX = re.compile(
        r'^\[(?P<window_id>\d+):(?P<tab_id>\d+)\] +(?P<content>.+)'
    )

    def activate(self, tab_id):
        self._run('activate', '-t', tab_id)

    def list_links(self):
        return self._list('links')

    def list_tabs(self):
        return self._list('tabs')

    def _list(self, what):
        assert what in {'tabs', 'links'}
        output = self._run('list', what)
        return (
            self._parse_tab_line(line.strip())
            for line in output.splitlines()
        )

    def _parse_tab_line(self, line):
        line = line.decode('utf-8')
        return self.TAB_REGEX.match(line).groupdict()

    def _run(self, *commands):
        return subprocess.check_output(('chrome-cli',) + commands)


def open_url(url):
    chrome_cli = ChromeCli()
    try:
        tab = next(
            tab
            for tab in chrome_cli.list_links()
            if tab['content'] == url)
    except StopIteration:
        return webbrowser.open(url)
    else:
        chrome_cli.activate(tab['tab_id'])
        subprocess.check_call([
            'osascript', '-e', 'activate application "Google Chrome"'
        ])
