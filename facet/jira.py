from enum import Enum

from clint.textui import colored


class Status(Enum):
    todo = 1
    doing = 2
    done = 3


JIRA_STATUS2STATUS = {
    'Closed': Status.done,
    'Review': Status.doing,
    'To Do': Status.todo,
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

    def colored(self, string):
        color_fn = {
            Status.todo: None,
            Status.doing: colored.red,
            Status.done: colored.green,
        }[self.status]
        return color_fn(string) if color_fn else string
