import logging
import socket
import json
from random import choice

from six.moves.xmlrpc_client import ServerProxy as XMLRPCServer

from tornado.iostream import StreamClosedError
from tornado.tcpclient import TCPClient
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado import gen, escape

logger = logging.getLogger(__name__)

try:
    import tornadis
except ImportError:
    logger.warn(
        "Unable to import tornadis. RedisCheckers will raise exceptions.")

try:
    import msgpack
except ImportError:
    msgpack = None


class Checker(object):
    """Base class for all checkers. Subclass this class to define your
    own checkers.

    """
    def check(self):
        """Override this method to check the status of an arbitrary
        system. This method should return a boolean, or at least
        something that behaves sensibly as one.

        It is highly recommended, though not required, to implement
        :meth:`check` as a Tornado coroutine in order to minimize
        blocking.

        """
        raise NotImplementedError("The check method must be implemented.")


class DummyChecker(Checker):
    """A fake checker used for testing. This will either randomly
    return True or False, or always return one or the other if the
    keyword argument ``return_value`` is set.

    """
    def __init__(self, return_value=None):
        assert isinstance(return_value, bool) or return_value is None
        self.return_value = return_value

    def check(self):
        if self.return_value is None:
            return choice([True, False])
        else:
            return self.return_value


class PortChecker(Checker):
    """Check if a TCP port is open.

    Note that this is somewhat of a hack and will only work properly
    if firewall rules allow it.

    """
    def __init__(self, host, port):
        """Configure a port checker.

        :param str host:
        :param int port:

        """
        assert isinstance(host, str)
        assert isinstance(port, int)
        self.host = host
        self.port = port

    @gen.coroutine
    def check(self):
        status = False
        try:
            conn = yield TCPClient().connect(self.host, self.port)
            conn.close()
            status = True
        except socket.gaierror:
            pass
        except StreamClosedError:
            pass
        except Exception as e:
            logger.error('Exception: ' + str(e))
        raise gen.Return(status)


class HttpChecker(Checker):
    """Check if an HTTP response (for a GET request) returns 200
    (OK).

    :param str url: URL to check
    :param float timeout: timeout in seconds

    """
    def __init__(self, url, timeout=1.5):
        assert isinstance(url, str)
        assert isinstance(timeout, (int, float))
        self.url = url
        self.timeout = timeout

    @gen.coroutine
    def check(self):
        try:
            res = yield AsyncHTTPClient().fetch(
                HTTPRequest(self.url, request_timeout=self.timeout))
            ok = True if res.code == 200 else False
        except socket.gaierror:
            ok = False
        except HTTPError:
            ok = False
        raise gen.Return(ok)


class SupervisorChecker(Checker):
    """Check that a process running via a supervisord instance is
    running.

    See the supervisor_ documentation on how to configure
    ``supervisord`` to accept XMLRPC requests over HTTP.

    .. _supervisor: http://supervisord.org/

    :param str host: hostname of the XMLRPC server
    :param str name: the process name to check

    """
    def __init__(self, host, name):
        assert isinstance(host, str)
        self.server = XMLRPCServer(host)
        assert isinstance(name, str)
        self.name = name

    @gen.coroutine
    def check(self):
        # TODO: make async query
        try:
            reply = self.server.supervisor.getProcessInfo(self.name)
            if 'statename' in reply:
                result = True if reply['statename'] == 'RUNNING' else False
        except Exception as error:
            logger.error(str(error))
            result = False
        raise gen.Return(result)


class JsonChecker(Checker):
    """Check that one or more keys has a particular value in an HTTP
    JSON response.

    If multiple keys/values are specified, the result of the check
    will only be True if *all* key/value pairs match the input
    dictionary.

    :param str url: URL to get JSON response from
    :param dict dictionary: compare keys/values with the JSON response

    """
    def __init__(self, url, dictionary):
        assert isinstance(url, str)
        assert isinstance(dictionary, dict)
        self.url = url
        self.dictionary = dictionary

    @gen.coroutine
    def check(self):
        result = True
        try:
            res = yield AsyncHTTPClient().fetch(self.url)
        except socket.gaierror:
            logger.warn('Unable to connect to ' + self.url)
            result = False
        try:
            obj = json.loads(escape.to_basestring(res.body))
        except ValueError:
            logger.error('No JSON found at URL ' + self.url)
            result = False
        for key in self.dictionary:
            try:
                if obj[key] != self.dictionary[key]:
                    result = False
            except KeyError:
                result = False
        raise gen.Return(result)


class RedisChecker(Checker):
    """Check that one or more keys have certain values in a Redis
    database.


    :param str host: Redis hostname
    :param dict dictionary: dictionary to match Redis keys/values
    :param **redis_kwargs: kwargs to pass to the Redis constructor

    """
    def __init__(self, host, dictionary, **redis_kwargs):
        self.db = tornadis.Client(host=host, **redis_kwargs)
        assert isinstance(dictionary, dict)
        self.dictionary = dictionary

    @gen.coroutine
    def check(self):
        result = True
        for key in self.dictionary:
            try:
                value = yield self.db.call('GET', key)
                if self.dictionary[key] != value:
                    result = False
            except KeyError:
                result = False
        raise gen.Return(result)


class SerializedRedisChecker(RedisChecker):
    """Check multiple key/value pairs that are serialized into a single
    Redis key/value pair with either JSON or msgpack.

    """
    def __init__(self, host, key, packing, dictionary, **redis_kwargs):
        super(SerializedRedisChecker, self).__init__(
            host, dictionary, **redis_kwargs)
        self.key = key
        packing = packing.lower()
        assert packing in ['json', 'msgpack']
        if packing == 'msgpack' and msgpack is None:
            raise RuntimeError(
                'Please install msgpack for unpacking msgpack-packed things.')
        self.packing = packing

    @gen.coroutine
    def check(self):
        result = False
        packed = yield self.db.call('GET', self.key)
        kind = json if self.packing == 'json' else msgpack
        unpacked = kind.loads(packed)
        for key in self.dictionary:
            try:
                if self.dictionary[key] == unpacked[key]:
                    result = True
            except KeyError:
                logger.error("Invalid key: " + key)
        raise gen.Return(result)


# Aliases for convenience
HTTPChecker = HttpChecker
JSONChecker = JsonChecker
