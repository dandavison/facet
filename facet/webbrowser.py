import re
import subprocess
import webbrowser
from textwrap import dedent


class Chrome:
    # Example line of `chrome-cli list tabs` output:
    # [1794:2294] python parsimonious - Google Search
    TAB_REGEX = re.compile(r'''
    ^
    \[
      (?P<window_id>\d+)
      :
      (?P<tab_id>\d+)
    \]
    \s+
    (?P<content>.+)
    ''', re.VERBOSE)

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

    def get_tab_and_window_index(self, tabs, predicate):
        """
        Return first parsed tab matching predicate, and index of tab's window.

        Input is a list of tab dicts (as returned by `list_tabs` or
        `list_links`, and a tab predicate function. The sequence of window IDs
        in the tab list is assumed to reflect the window index recognized by
        the OS (Window Manager). I.e., a list of tabs

        [{'window_id': 1634}, {'window_id': 1634}, {'window_id': 1748}]

        would be assumed to represent two tabs with window index 1 and one tab
        with window index 2.
        """
        window_index = 0
        window_id = None
        for tab in tabs:
            if tab['window_id'] != window_id:
                window_index += 1
                window_id = tab['window_id']
            if predicate(tab):
                return tab, window_index
        raise StopIteration

    def raise_tab(self, tab, window_index):
        """
        Activate tab and raise tab's window.
        """
        self.activate(tab['tab_id'])
        script = dedent("""
        tell application "System Events" to tell process "Google Chrome"
            perform action "AXRaise" of window {window_index}
            set frontmost to true
        end tell
        """).format(window_index=window_index)
        proc = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate(script.encode('utf-8'))
        assert not stderr, stderr


def open_url(url):
    chrome = Chrome()
    tabs = chrome.list_links()
    try:
        tab, window_index = chrome.get_tab_and_window_index(
            tabs,
            lambda tab: tab['content'] == url,
        )
    except StopIteration:
        webbrowser.open(url)
    else:
        chrome.raise_tab(tab, window_index)
