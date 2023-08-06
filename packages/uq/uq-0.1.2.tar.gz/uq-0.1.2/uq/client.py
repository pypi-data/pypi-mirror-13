# coding: utf-8

import etcd

from .exceptions import UqError, UqNotImplementedError
from .consts import ProtocolHttp, ProtocolMemcache, ProtocolRedis
from .conn import HttpConn, RedisConn, MemcacheConn


class Client(object):
    '''
    Base class of client for the uq library.
    '''

    def __init__(self, protocol):
        if protocol not in [ProtocolHttp, ProtocolRedis, ProtocolMemcache]:
            raise UqError('invalid protocol: {}'.format(protocol))
        self.protocol = protocol
        self._init_uq_conn()

    def _init_uq_conn(self):
        raise UqNotImplementedError

    def add(self, topic, line=None, recycle=None):
        return self.conn.add(topic, line, recycle)

    def push(self, key, value):
        return self.conn.push(key, value)

    def pop(self, key):
        return self.conn.pop(key)

    def remove(self, key):
        return self.conn.remove(key)


class UqClient(Client):
    '''
    Client implementation for communication with standalone uq server
    '''

    def __init__(self, protocol='http', ip='localhost', port=8808, **kwargs):
        self._ip = ip
        self._port = port
        self._kwargs = kwargs
        super(UqClient, self).__init__(protocol)

    def _init_uq_conn(self):
        addr = '{ip}:{port}'.format(ip=self._ip, port=self._port)
        if self.protocol == ProtocolHttp:
            self.conn = HttpConn(addr, None, None)
        elif self.protocol == ProtocolRedis:
            self.conn = RedisConn(addr, None, None)
        elif self.protocol == ProtocolMemcache:
            self.conn = MemcacheConn(addr, None, None)
        else:
            raise UqError('invalid protocol: {}'.format(self.protocol))


class UqClusterClient(Client):
    '''
    Client implementation for communication with uq cluster
    '''

    def __init__(self, protocol='http', etcd_host='127.0.0.1', etcd_port=4001,
                 etcd_key='uq', **kwargs):
        self._etcd_host = etcd_host
        self._etcd_port = etcd_port
        self._etcd_key = etcd_key
        self._etcd_cli = None
        _kwargs = {}
        for k, v in kwargs.items():
            # use prefix '_etcd_' to avoid name confliction with
            # positional arguments
            if k.startswith('_etcd_'):
                k = k[len('_etcd_'):]
            _kwargs[k] = v
        self._kwargs = _kwargs
        super(UqClusterClient, self).__init__(protocol)

    @property
    def etcd_cli(self):
        if self._etcd_cli is None:
            self._etcd_cli = etcd.Client(
                host=self._etcd_host, port=self._etcd_port, **self._kwargs)
        return self._etcd_cli

    def _init_uq_conn(self):
        if self.protocol == ProtocolHttp:
            self.conn = HttpConn(None, self.etcd_cli, self._etcd_key)
        elif self.protocol == ProtocolRedis:
            self.conn = RedisConn(None, self.etcd_cli, self._etcd_key)
        elif self.protocol == ProtocolMemcache:
            self.conn = MemcacheConn(None, self.etcd_cli, self._etcd_key)
        else:
            raise UqError('invalid protocol: {}'.format(self.protocol))
