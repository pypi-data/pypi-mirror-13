from __future__ import unicode_literals

import codic


class Executor(object):
    def __init__(self, config):
        super(Executor, self).__init__()
        self.config = config

    def get_translations(self, text, persist_config=True):
        api = codic.API(self.config)
        result = api.get_translations(text)
        if persist_config:
            self.config.persist()
        return result

    def print_translations(self, text, persist_config=True):
        result = self.get_translations(text, persist_config)
        print(codic.Formatter.get(self.config.format).format(result))
