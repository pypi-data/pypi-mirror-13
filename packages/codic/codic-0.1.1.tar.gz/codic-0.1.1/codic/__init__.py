from codic.api import API
from codic.config import Config
from codic.cli import CLIParser
from codic.executor import Executor
from codic.formatter import Formatter

CASES = ['camel', 'pascal', 'lower underscore', 'upper underscore', 'hyphen']

class CodicException(Exception):
    pass
