from clint.textui import colored

from facet.core import Status
from facet.utils import default_color


JIRA_STATUS2STATUS = {
    'Open': Status.todo,
    'To Do': Status.todo,
    'Groomed': Status.todo,
    'In Progress': Status.doing,
    'Review': Status.under_review,
    'Closed': Status.done,
    'Reopened': Status.todo,
    'Done': Status.done,
}


class JiraIssue:
    def __init__(self, json):
        self.json = json

    @property
    def summary(self):
        return self.json['fields']['summary']

    @property
    def jira_status(self):
        return self.json['fields']['status']['name']

    @property
    def status(self):
        return JIRA_STATUS2STATUS[self.jira_status]

    @property
    def is_done(self):
        return self.status == Status.done
