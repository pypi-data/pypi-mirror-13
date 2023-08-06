import contextlib
import logging
import re
import shutil
import ssl
import urllib


logger = logging.getLogger(__name__)
re_filename = re.compile(r"filename=(.+)")


class DownloadApiMixin(object):
    def download(self, token, **kwargs):
        context = ssl.create_default_context()
        if not self.session.verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return urllib.request.urlopen(
            urllib.request.Request('{0}/download/{1}'.format(self.url, token),
                **kwargs), context=context)

    def save(self, token):
        with contextlib.closing(self.download(token, method='HEAD')) as head:
            headers = head.info()
            length = int(headers['content-length'])
            filename = urllib.parse.unquote(
                re_filename.search(headers['content-disposition']).group(1))
        with open(filename, 'ab') as fh:
            offset = fh.tell()
            if offset < length:
                with contextlib.closing(self.download(token, headers={
                            'Range': "bytes={0}-".format(offset),
                        })) as get:
                    shutil.copyfileobj(get, fh)
        return filename
