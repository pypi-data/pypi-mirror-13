import logging

from kidibox.session import Session
from kidibox import api


logger = logging.getLogger(__name__)


class Client(api.AuthApiMixin, api.TorrentsApiMixin, api.DownloadApiMixin):
    session_class = Session

    def __init__(self, url, username, password, verify=None):
        self.session = self.session_class(verify=verify)
        self.url = url
        self.username = username
        self.password = password

    def __repr__(self):
        return 'Client(url={url!r}, username={username!r})'\
            .format(url=self.url, username=self.username)

    def _make_request(self, method, path, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.is_authenticated():
            kwargs['headers']['Authorization'] = "Bearer " + self.session.token
        url = "{base_url}{path}".format(base_url=self.url, path=path)
        caller = getattr(self.session, method)
        return caller(url, **kwargs)

    def _get(self, path, **kwargs):
        return self._make_request('get', path, **kwargs)

    def _post(self, path, **kwargs):
        return self._make_request('post', path, **kwargs)

    def is_authenticated(self):
        return self.session.is_authenticated()
