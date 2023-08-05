import requests

import codic


class API(object):
    BASE_ENDPOINT = 'https://api.codic.jp'

    def __init__(self, config):
        super(API, self).__init__()
        self.config = config
        self._validate_config()

    def _validate_config(self):
        if not self.config.token:
            raise codic.CodicException('No token provided.')
        if self.config.casing not in codic.CASES:
            raise codic.CodicException('Invalid case provided: {0}. Available cases are {1}'.format(
                self.config.casing, ', '.join(codic.CASES)))

    def get_translations(self, base_text):
        query = {'text': base_text, 'casing': self.config.casing}
        url = self.url('/v1/engine/translate.json')
        res = requests.get(url, params=query, headers=self.auth_headers)
        if res.status_code != 200:
            raise codic.CodicException(res.json()['errors'][0]['message'])
        return {w['text']: [c['text'] for c in w['candidates']]
                for v in res.json()
                for w in v['words']}

    def url(self, path):
        return API.BASE_ENDPOINT + path

    @property
    def auth_headers(self):
        return {'Authorization': 'Bearer {0}'.format(self.config.token)}
