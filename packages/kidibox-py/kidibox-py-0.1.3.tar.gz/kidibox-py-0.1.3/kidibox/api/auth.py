import logging


logger = logging.getLogger(__name__)


class AuthApiMixin(object):
    def register(self):
        return self._post('/register', json={
            'username': self.username,
            'password': self.password,
        }).json()

    def authenticate(self):
        response = self._post('/authenticate', json={
            'username': self.username,
            'password': self.password,
        }).json()
        self.session.token = response['token']
        return response
