from __future__ import print_function, division, absolute_import

from collections import defaultdict
import json
import logging

from tornado import web, gen
from tornado.httpclient import AsyncHTTPClient

from .core import RequestHandler, MyApp, Resources, Proxy
from ..utils import key_split


logger = logging.getLogger(__name__)


class Info(RequestHandler):
    """ Basic info about the scheduler """
    def get(self):
        resp = {'ncores': {'%s:%d' % k: n for k, n in self.server.ncores.items()},
                'status': self.server.status}
        self.write(resp)


class Processing(RequestHandler):
    """ Active tasks on each worker """
    def get(self):
        resp = {'%s:%d' % addr: list(map(key_split, tasks))
                for addr, tasks in self.server.processing.items()}
        self.write(resp)


class Broadcast(RequestHandler):
    """ Send REST call to all workers, collate their responses """
    @gen.coroutine
    def get(self, rest):
        addresses = [(ip, port, d['http'])
                     for (ip, port), d in self.server.worker_services.items()
                     if 'http' in d]
        client = AsyncHTTPClient()
        responses = {'%s:%d' % (ip, tcp_port): client.fetch("http://%s:%d/%s" %
                                                  (ip, http_port, rest))
                     for ip, tcp_port, http_port in addresses}
        responses2 = yield responses
        responses3 = {k: json.loads(v.body.decode())
                      for k, v in responses2.items()}
        self.write(responses3)  # TODO: capture more data of response


class MemoryLoad(RequestHandler):
    """The total amount of data held in memory by workers"""
    def get(self):
        out = {}
        for worker, keys in self.server.has_what.items():
            out["%s:%s"%worker] = sum(self.server.nbytes[k] for k in keys)
        self.write(out)


class MemoryLoadByKey(RequestHandler):
    """The total amount of data held in memory by workers"""
    def get(self):
        out = {}
        for worker, keys in self.server.has_what.items():
            d = defaultdict(lambda: 0)
            for key in keys:
                d[key_split(key)] += self.server.nbytes[key]
            out["%s:%d" % worker] = dict(d)
        self.write(out)


def HTTPScheduler(scheduler):
    application = MyApp(web.Application([
        (r'/info.json', Info, {'server': scheduler}),
        (r'/resources.json', Resources, {'server': scheduler}),
        (r'/processing.json', Processing, {'server': scheduler}),
        (r'/proxy/([\w.-]+):(\d+)/(.+)', Proxy),
        (r'/broadcast/(.+)', Broadcast, {'server': scheduler}),
        (r'/memory-load.json', MemoryLoad, {'server': scheduler}),
        (r'/memory-load-by-key.json', MemoryLoadByKey, {'server': scheduler}),
        ]))
    return application
