# coding: utf-8

import sys
import random
import logging
import functools

import etcd
import redis
import requests
from pymemcache.client.base import Client as McClient
from pymemcache.exceptions import MemcacheError, MemcacheClientError

from .exceptions import UqError, UqNotImplementedError
from .consts import MaxRetry
from .utils import timedetla_to_str


def query_addrs(etcd_cli, etcd_key):
    try:
        resp = etcd_cli.read(
            '/{}/servers'.format(etcd_key), sorted=True, recursive=False)
    except etcd.EtcdKeyNotFound as e:
        logging.error('server entrypoint not found: {}'.format(e))
        raise
    except etcd.EtcdConnectionFailed as e:
        logging.error('failed to connect etcd: {}'.format(e))
        raise

    if not resp.dir:
        raise UqError('invalid etcd key')
    for child in resp.children:
        yield child.key.split('/')[-1]


class Conn(object):
    '''
    Base class of connection from uq client to uq server.
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        self.addr = addr
        self.etcd_cli = etcd_cli
        self.etcd_key = etcd_key
        self.addrs = None
        self._update_conn_pool()

    def _choose(self):
        if len(self.addrs) == 0:
            return None
        return random.choice(self.addrs)

    def _update_conn_pool(self):
        raise UqNotImplementedError

    def _add(self, addr, data):
        raise UqNotImplementedError

    def _push(self, addr, data):
        raise UqNotImplementedError

    def _pop(self, addrs, data):
        raise UqNotImplementedError

    def _remove(self, addr, data):
        raise UqNotImplementedError

    def add(self, topic, line, recycle):
        if not topic:
            raise UqError('topic is empty')
        updated = False
        while True:
            retry = 0
            while retry < MaxRetry:
                addr = self._choose()
                data = {
                    'topic': topic,
                    'line': line,
                    'recycle': timedetla_to_str(recycle),
                }
                if addr is None:
                    logging.error('no uq server available')
                else:
                    result = self._add(addr, data)
                if result is None:
                    retry += 1
                else:
                    return result

            if not updated:
                self._update_conn_pool()
                updated = True
            else:
                break

        return False, 'all conn add failed after retry'

    def push(self, key, value):
        updated = False
        while True:
            retry = 0
            while retry < MaxRetry:
                addr = self._choose()
                if addr is None:
                    logging.error('no uq server available')
                else:
                    data = {
                        'key': key,
                        'value': value,
                    }
                    result = self._push(addr, data)
                    if result is None:
                        retry += 1
                    else:
                        return result
                retry += 1

            if not updated:
                self._update_conn_pool()
                updated = True
            else:
                break

        return False, 'all conn push failed after retry'

    def pop(self, key):
        updated = False
        while True:
            retry = 0
            while retry < MaxRetry:
                data = {'key': key}
                result = self._pop(self.addrs, data)
                if result is None:
                    retry += 1
                else:
                    return result

            if not updated:
                self._update_conn_pool()
                updated = True
            else:
                break

        return False, '', 'all conn pop failed after retry'

    def remove(self, key):
        values = key.split('/', 1)
        if len(values) != 2:
            return False, 'key illegal'
        addr, cid = values

        retry = 0
        while retry < MaxRetry:
            data = {'cid': cid}
            result = self._remove(addr, data)
            if result is None:
                retry += 1
            else:
                return result
            retry += 1

        return False, 'all conn del failed after retry'


def catch_requests_error(func):
    @functools.wraps(func)
    def wrap_f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logging.error('requests error: {}'.format(e))
            return None
    return wrap_f


class HttpConn(Conn):
    '''
    Http protocol based connection between uq client and uq server
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        super(HttpConn, self).__init__(addr, etcd_cli, etcd_key)

    def _update_conn_pool(self):
        if self.etcd_cli is None:
            self.addrs = [self.addr]
        else:
            self.addrs = [x for x in query_addrs(self.etcd_cli, self.etcd_key)]

    @catch_requests_error
    def _add(self, addr, data):
        url = 'http://{0}/v1/queues'.format(addr)
        r = requests.put(url, data)
        if r.status_code == requests.codes.created:
            return True, ''
        else:
            if 'Existed' in r.text:
                return False, r.text
            logging.error('add error: {}'.format(r.text))
            return None

    @catch_requests_error
    def _push(self, addr, data):
        key = data.pop('key')
        url = 'http://{0}/v1/queues/{1}'.format(addr, key)
        r = requests.post(url, data)
        if r.status_code == requests.codes.no_content:
            return True, ''
        else:
            logging.error('push error: {}'.format(r.text))
            return None

    @catch_requests_error
    def _pop(self, addrs, data):
        nomsg = 0
        for addr in addrs:
            url = 'http://{0}/v1/queues/{1}'.format(addr, data['key'])
            r = requests.get(url)
            if r.status_code == requests.codes.not_found:
                nomsg += 1
            elif r.status_code == requests.codes.ok:
                cid = '{}/{}'.format(addr, r.headers.get('X-UQ-ID'))
                value = r.content
                return True, cid, value
            else:
                logging.error('pop error: {}'.format(r.text))
        if nomsg == len(addrs):
            return False, '', 'no message'
        return None

    @catch_requests_error
    def _remove(self, addr, data):
        url = 'http://{0}/v1/queues/{1}'.format(addr, data['cid'])
        r = requests.delete(url)
        if r.status_code == requests.codes.no_content:
            return True, ''
        else:
            logging.error('del error: {}'.format(r.text))
            return None


def catch_redis_error(func):
    @functools.wraps(func)
    def wrap_f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.RedisError as e:
            logging.error('redis error: {}'.format(e))
            return None
    return wrap_f


class RedisConn(Conn):
    '''
    RESP protocol based connection between uq client and uq server
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        super(RedisConn, self).__init__(addr, etcd_cli, etcd_key)

    def _update_conn_pool(self):
        if self.etcd_cli is None:
            self.addrs = [self.addr]
        else:
            self.addrs = [x for x in query_addrs(self.etcd_cli, self.etcd_key)]
        self.conns = {}
        for addr in self.addrs:
            try:
                host, port = addr.split(':')
            except ValueError:
                raise UqError('invalid rq address {}'.format(addr))
            self.conns[addr] = redis.StrictRedis(host=host, port=port)

    @catch_redis_error
    def _add(self, addr, data):
        if not data['line']:
            args = ['ADD', data['topic']]
        else:
            full_line_name = '{topic}/{line}'.format(**data)
            args = ['ADD', full_line_name, data['recycle']]

        try:
            r = self.conns[addr].execute_command(*args)
        except redis.exceptions.ResponseError as e:
            errstr = str(e)
            if 'Existed' in errstr:
                return False, errstr
            logging.error('add error: {}'.format(errstr))
            return None
        if r == b'OK':
            return True, ''
        return None

    @catch_redis_error
    def _push(self, addr, data):
        self.conns[addr].set(data['key'], data['value'])
        return True, ''

    @catch_redis_error
    def _pop(self, addrs, data):
        nomsg = 0
        for addr in addrs:
            try:
                r = self.conns[addr].execute_command('GET', data['key'])
                cid = '{}/{}'.format(addr, r[1].decode('utf-8'))
                value = r[0]
                return True, cid, value
            except redis.exceptions.ResponseError as e:
                if 'No Message' in str(e):
                    nomsg += 1
                else:
                    logging.error('pop error: {}'.format(e))
                    return None
        if nomsg == len(addrs):
            return False, '', 'no message'
        return None

    @catch_redis_error
    def _remove(self, addr, data):
        try:
            self.conns[addr].execute_command('DEL', data['cid'])
        except ValueError as e:
            # UQ returns 'OK' when messages(keys) were removed, while
            # the standard redis returns the number of successful removed
            # keys when executing DEL.
            if sys.version_info[0] < 3:
                if str(e) == "invalid literal for int() with base 10: 'OK'":
                    return True, ''
            else:
                if str(e) == "invalid literal for int() with base 10: b'OK'":
                    return True, ''
            raise
        return True, ''


def catch_memcache_error(func):
    @functools.wraps(func)
    def wrap_f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MemcacheError as e:
            logging.error('memcache error: {}'.format(e))
            return None
    return wrap_f


class MemcacheConn(Conn):
    '''
    Memcache protocol based connection between uq client and uq server
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        super(MemcacheConn, self).__init__(addr, etcd_cli, etcd_key)

    def _update_conn_pool(self):
        if self.etcd_cli is None:
            self.addrs = [self.addr]
        else:
            self.addrs = [x for x in query_addrs(self.etcd_cli, self.etcd_key)]
        self.conns = {}
        for addr in self.addrs:
            try:
                host, port = addr.split(':')
                port = int(port)
            except ValueError:
                raise UqError('invalid rq address {}'.format(addr))
            self.conns[addr] = McClient((host, port))

    @catch_memcache_error
    def _add(self, addr, data):
        if not data['line']:
            key = data['topic']
            value = ''
        else:
            key = '{topic}/{line}'.format(**data)
            value = data['recycle']
        self.conns[addr].add(key, value)
        return True, ''

    @catch_memcache_error
    def _push(self, addr, data):
        self.conns[addr].set(data['key'], data['value'])
        return True, ''

    @catch_memcache_error
    def _pop(self, addrs, data):
        nomsg = 0
        for addr in addrs:
            try:
                key = data['key']
                r = self.conns[addr].get_many([key, 'id'])
                cid = '{}/{}'.format(addr, r['id'].decode('utf-8'))
                value = r[key]
                return True, cid, value
            except MemcacheClientError as e:
                if 'No Message' in str(e):
                    nomsg += 1
                else:
                    logging.error('pop error: {}'.format(e))
                    return None
        if nomsg == len(addrs):
            return False, '', 'no message'
        return None

    @catch_memcache_error
    def _remove(self, addr, data):
        self.conns[addr].delete(data['cid'])
        return True, ''
