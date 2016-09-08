import socket
import binascii
import logging

from .context import slowjam_context

logger = logging.getLogger(__name__)


class DummySocket(object):

    def sendto(self, value, addr):
        pass


class StatsdClient(object):
    """A very basic client for aggregating application stats to statsd/graphite

    Some guiding ideas:
    1- Always log stats to a bucket based on the current machine (and region)
    2- Most stats are based on the current application and evironment so make that the default prefix
    3- Some metrics don't fit neatly within an application bucket (ex: size of message queues). Allow overriding the
    prefix/bucket so the stat gets logged to somewhere other than #2
    """

    def __init__(self, hosts, prefix, socket_builder=None):

        self.sock = socket_builder() or socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        addrs = []
        for host in hosts:
            host, port = host.split(':', 1)
            port = int(port)
            addrs.append((socket.gethostbyname(host), port))

        self.addrs = addrs
        self.count = len(addrs)
        self.prefix = prefix

    def get_addr(self, stat):
        return self.addrs[(binascii.crc32(stat) & 0xffffffff) % self.count]

    def make_prefix(self, prefix):
        if prefix is None:
            return self.prefix
        else:
            return prefix

    def graphite_duration(self, stat, elapsed_time, prefix=None, fmt=None, extras=None):
        try:
            self.sock.sendto('all.%s.%s:%d|ms' % (self.make_prefix(prefix), stat, elapsed_time), self.get_addr(stat))
        except:
            logger.exception('Dropping graphite_duration stat=%s on floor:', stat)

    def graphite_count(self, stat, delta, prefix=None, fmt=None, extras=None):
        try:
            self.sock.sendto('all.%s.%s:%d|c' % (self.make_prefix(prefix), stat, delta), self.get_addr(stat))
        except:
            logger.exception('Dropping graphite_count=%s on floor:', stat)

    def graphite_gauge(self, stat, value, prefix=None):
        # n.b., you should probably only use these from guaranteed-unique tasks
        try:
            self.sock.sendto('all.%s.%s:%d|g' % (self.make_prefix(prefix), stat, value), self.get_addr(stat))
        except:
            logger.exception('Dropping graphite_gauge=%s on floor:', stat)

    def graphite_set(self, stat, value, prefix=None):
        # only put id-like values in here
        try:
            self.sock.sendto('all.%s.%s:%s|s' % (self.make_prefix(prefix), stat, value), self.get_addr(stat))
        except:
            logger.exception('Dropping graphite_set=%s on floor:', stat)


_instance = None


def configure_statsd(hosts=['localhost:8125'], app='unknown', environment='unknown'):
    global _instance
    _instance = StatsdClient(hosts, app, environment)


def graphite_duration(stat, elapsed_time, prefix=None):
    # TODO: Hook this up to slowjam?
    if _instance:
        _instance.graphite_duration(stat, elapsed_time, prefix)


def graphite_count(stat, delta=1, prefix=None, fmt=None, extras=None, tag=None):
    slowjam_context.mark(stat, fmt, extras, tag)
    if _instance:
        _instance.graphite_count(stat, delta, prefix)


def graphite_increment(stats, prefix=None):
    graphite_count(stats, 1, prefix)


def graphite_decrement(stats, prefix=None):
    graphite_count(stats, -1, prefix)


def graphite_gauge(stat, value, prefix=None):
    if _instance:
        _instance.graphite_gauge(stat, value, prefix=prefix)


def graphite_set(stat, value, prefix=None):
    if _instance:
        _instance.graphite_set(stat, value, prefix=prefix)
