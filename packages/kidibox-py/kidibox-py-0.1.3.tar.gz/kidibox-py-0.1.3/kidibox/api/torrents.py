import logging

from .decorators import requires_authentication


logger = logging.getLogger(__name__)


class TorrentsApiMixin(object):
    @requires_authentication
    def list(self):
        return self._get('/torrents').json()

    @requires_authentication
    def create(self, link):
        return self._post('/torrents/link', json={
            'link': link,
        }).json()

    @requires_authentication
    def get(self, id):
        return self._get('/torrents/{0}'.format(id)).json()

    @requires_authentication
    def get_token(self, id, file_index):
        return self._get(
            '/torrents/{0}/files/{1}/token'.format(id, file_index)).json()
