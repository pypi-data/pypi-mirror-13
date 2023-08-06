import logging

from kidibox.client import Client


__author__ = 'Cecile Tonglet'
__version__ = '0.1.3'


def set_stream_logger(
        name='kidibox', level=logging.DEBUG, format_string=None):
    """
    Add a stream handler for the given name and level to the logging module.
    By default, this logs all kidibox messages to ``stdout``.
        >>> import kidibox
        >>> kidibox.set_stream_logger('kidibox.client', logging.INFO)
    :type name: string
    :param name: Log name
    :type level: int
    :param level: Logging level, e.g. ``logging.INFO``
    :type format_string: str
    :param format_string: Log message format
    """
    if format_string is None:
        format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def connect(*args, **kwargs):
    return Client(*args, **kwargs)


logging.getLogger('kidibox').addHandler(logging.NullHandler())
