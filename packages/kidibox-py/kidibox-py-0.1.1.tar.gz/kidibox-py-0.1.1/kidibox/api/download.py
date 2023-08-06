import logging
import re


logger = logging.getLogger(__name__)
re_filename = re.compile(r"filename=(.+)")


class DownloadApiMixin(object):
    def download(self, token, **kwargs):
        response = self._get('/download/{0}'.format(token), stream=True)
        return (
            re_filename.search(
                response.headers['content-disposition']).group(1),
            response.iter_content(**kwargs))
