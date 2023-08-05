import argparse
import sys

import codic


class CLIParser(argparse.ArgumentParser):
    def __init__(self):
        super(CLIParser, self).__init__()
        self.description = 'get name from codic API'
        self.add_argument(
            'text',
            metavar='TEXT',
            type=str,
            help='the text to translate'
        )
        self.add_argument(
            '-t',
            '--token',
            type=str,
            help='Codic API token'
        )
        self.add_argument(
            '-c',
            '--casing',
            choices=[k.replace(' ', '-') for k in codic.CASES],
            help='Casing for the generated variable'
        )
        self.add_argument(
            '-f',
            '--format',
            choices=['text', 'json'],
            help='Choose the output format'
        )

    @staticmethod
    def run(args=None):
        context = CLIParser().parse_args(args)
        config = codic.Config(vars(context))
        try:
            codic.Executor(config).print_translations(context.text)
        except codic.CodicException as ex:
            print('An error occurred: {0}'.format(ex))
            sys.exit(1)
