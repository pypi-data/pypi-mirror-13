# Module:   utils
# Date:     16th November 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Utilities"""


from urlparse import urlparse


def format_url(ip, port):
    port = "" if port in (80, 443) else ":{0:d}".format(port)
    scheme = "https" if port == 443 else "http"
    url = "{0:s}://{1:s}{2:s}".format(scheme, ip, port)
    return url


def parse_redis_url(url):
    parsed = urlparse(url)

    netloc = parsed.netloc
    if "@" in netloc:
        creds, host = netloc.split("@")
        _, password = creds.split(":")
    else:
        host = netloc
        password = None

    host, port = host.split(":")

    if parsed.path:
        database = int(parsed.path.replace("/", ""))
    else:
        database = 0

    return host, port, password, database
