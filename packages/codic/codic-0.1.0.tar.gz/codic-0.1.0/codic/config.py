import os
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

class Config(object):
    CODIC_SETTINGS_FILE = os.environ.get('CODIC_CONFIG_PATH', os.path.expanduser('~/.codicrc'))
    DEFAULTS = {
        'token': None,
        'casing': 'camel',
        'format': 'text'
    }

    def __init__(self, config = None):
        super(Config, self).__init__()
        self.config = Config.DEFAULTS.copy()
        file_config = self._config_from_file()
        if file_config:
            self._merge_config(file_config)
        if config:
            self._merge_config(config)

    def _config_from_file(self):
        if not os.path.exists(Config.CODIC_SETTINGS_FILE):
            return None
        config = ConfigParser()
        config.read(Config.CODIC_SETTINGS_FILE)
        if config.has_section('codic'):
            return dict(config.items('codic'))

    def _merge_config(self, config):
        for k, v in config.items():
            if k in Config.DEFAULTS and v:
                self.config[k] = v

    def persist(self):
        config = ConfigParser()
        config.read_dict({'codic': self.config})
        with open(Config.CODIC_SETTINGS_FILE, 'w') as f:
            config.write(f)

    @property
    def token(self):
        return self.config.get('token')

    @property
    def casing(self):
        return self.config.get('casing').replace('-', ' ')

    @property
    def format(self):
        return self.config.get('format')
