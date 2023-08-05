try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import redis


def connect(url):
    """
    Connect to the given redis url

    :param url: string - e.g. redis://docker.local:45159/0
    :return:
    """
    url_parsed = urlparse(url)

    _redis = redis.StrictRedis(host=url_parsed.hostname, port=url_parsed.port, db=url_parsed.path[1:])

    return _redis
