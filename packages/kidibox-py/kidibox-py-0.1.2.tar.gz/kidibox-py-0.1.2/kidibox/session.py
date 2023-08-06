import logging
import requests

from kidibox.exceptions import ApiError


logger = logging.getLogger(__name__)


class Session(requests.Session):
    def __init__(self, verify=None, token=None):
        super(Session, self).__init__()
        if verify is not None:
            self.verify = verify
        self.token = token

    def is_authenticated(self):
        return (self.token is not None)

    def raise_for_status(self, response):
        if 400 <= response.status_code < 500:
            raise ApiError(
                "Error {0}".format(response.status_code), response=response)
        else:
            response.raise_for_status()

    def get(self, url, **kwargs):
        logger.debug(
            "Making GET request for %s (verify=%s)", url, self.verify)
        response = super(Session, self).get(url, **kwargs)
        self.raise_for_status(response)
        return response

    def post(self, url, **kwargs):
        logger.debug(
            "Making POST request for %s (verify=%s)", url, self.verify)
        response = super(Session, self).post(url, **kwargs)
        self.raise_for_status(response)
        return response
