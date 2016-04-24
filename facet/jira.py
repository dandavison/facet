class JiraIssue:
    def __init__(self, json):
        self.json = json

    @property
    def summary(self):
        return self.json['fields']['summary']
