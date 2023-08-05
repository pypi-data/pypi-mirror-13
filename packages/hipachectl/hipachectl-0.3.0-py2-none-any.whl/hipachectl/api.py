# Module:   api
# Date:     16th November 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""API"""


from redis import StrictRedis


from .utils import format_url, parse_redis_url


class Hipache(object):

    def __init__(self, url):
        host, port, password, database = parse_redis_url(url)

        self.r = StrictRedis(host=host, port=port, db=database, password=password)

    def __iter__(self):
        for i, k in enumerate(self.r.keys()):
            vhost = k.split(":")[1]
            xs = self.r.lrange(k, 0, -1)
            if len(xs) == 2:
                id, url = xs
                yield {"id": id, "host": vhost, "url": url}

    def add(self, id, host, ip, port):
        url = format_url(ip, port)
        vhost = "frontend:{0:s}".format(host)
        if vhost in self.r.keys():
            members = self.r.lrange(vhost, 0, -1)
            if id in members:
                if url not in members:
                    self.r.linsert(vhost, "after", id, url)
            else:
                self.r.rpush(vhost, id)
                self.r.rpush(vhost, url)
        else:
            self.r.rpush(vhost, id)
            self.r.rpush(vhost, url)

    def delete(self, id, host, ip, port):
        vhost = "frontend:{0:s}".format(host)
        if not ip:
            self.r.delete(vhost, id)
        else:
            url = format_url(ip, port)
            self.r.lrem(vhost, 0, url)
