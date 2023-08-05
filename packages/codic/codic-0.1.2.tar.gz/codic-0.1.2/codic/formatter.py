from __future__ import unicode_literals

import json


class Formatter(object):
    def format(self, result):
        raise NotImplementedError('not implemented')

    @classmethod
    def register(cls, name, formatter):
        if not hasattr(cls, 'formatters'):
            cls.formatters = {}
        cls.formatters[name] = formatter

    @classmethod
    def get(cls, name):
        return cls.formatters[name]()


class TextFormatter(Formatter):
    def format(self, result):
        return '\n'.join('{0}: {1}'.format(word, ', '.join([c for c in choices if c]))
                         for word, choices in result.items())

Formatter.register('text', TextFormatter)


class JSONFormatter(Formatter):
    def format(self, result):
        return json.dumps(result)

Formatter.register('json', JSONFormatter)
