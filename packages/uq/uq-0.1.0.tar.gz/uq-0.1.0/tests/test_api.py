# coding: utf-8

import unittest
import datetime

import uq


class TestUqClientApi(unittest.TestCase):

    def check_default_resp(self, resp):
        self.assertIsInstance(resp, tuple)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0], True)
        self.assertEqual(resp[1], '')

    def _test_api(self, protocol, port):
        cli = uq.UqClient(protocol=protocol, ip='localhost', port=port)
        r = cli.add('foo')
        self.check_default_resp(r)

        r = cli.add('foo', 'x', datetime.timedelta(seconds=10))
        self.check_default_resp(r)

        r = cli.push('foo', 'hello')
        self.check_default_resp(r)

        r = cli.pop('foo/x')
        self.assertEqual(r[2], b'hello')

        r = cli.remove(r[1])
        self.check_default_resp(r)

    def test_http_api(self):
        self._test_api(uq.ProtocolHttp, 8001)

    def test_redis_api(self):
        self._test_api(uq.ProtocolRedis, 8002)

    '''
    FIXME:
        pymemcache get_many command may rearrange the keys sequence,
        this leads uq library pop processing with error.
    '''
    # def test_memcache_api(self):
    #     self._test_api(uq.ProtocolMemcache, 8003)


class TestUqClusterApi(unittest.TestCase):

    def check_default_resp(self, resp):
        self.assertIsInstance(resp, tuple)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0], True)
        self.assertEqual(resp[1], '')

    def _test_api(self, protocol, etcd_host, etcd_port, etcd_key, **kwargs):
        cli = uq.UqClusterClient(protocol=protocol, etcd_host=etcd_host,
                                 etcd_port=etcd_port, etcd_key=etcd_key)
        r = cli.add('foo')
        self.check_default_resp(r)

        r = cli.add('foo', 'x', datetime.timedelta(seconds=10))
        self.check_default_resp(r)

        r = cli.push('foo', 'hello')
        self.check_default_resp(r)

        r = cli.pop('foo/x')
        self.assertEqual(r[2], b'hello')

        r = cli.remove(r[1])
        self.check_default_resp(r)

    def test_http_api(self):
        self._test_api('http', '127.0.0.1', 4001, 'uq')
