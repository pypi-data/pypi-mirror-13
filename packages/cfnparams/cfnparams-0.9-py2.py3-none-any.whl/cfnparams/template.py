import json


class Template(object):
    def __init__(self, filename):
        self.filename = filename

    def params(self):
        with open(self.filename, 'r') as fp:
            tmpl = json.load(fp)

        return set(tmpl['Parameters'].keys())
