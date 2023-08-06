# coding: utf-8

from collections import OrderedDict

from pymemcache.client.base import _readline, _readvalue, Client
from pymemcache.exceptions import MemcacheUnknownError


class MockMcClient(Client):

    def get_many(self, keys):
        """
        Mock function for get_many to fix uq pop bug temporarily.
        The uq pop processing in memcache protocol must receive the line-name
        as the first key, but pymemcache get_many command may rearrange the
        keys sequence, which leads uq library pop processing with error.

        Args:
            keys: list(str), see class docs for details.

        Returns:
            A dict in which the keys are elements of the "keys" argument list
            and the values are values from the cache. The dict may contain all,
            some or none of the given keys.
        """
        if not keys:
            return {}

        return self._mock_fetch_cmd(b'get', keys, False)

    def _mock_fetch_cmd(self, name, keys, expect_cas):
        checked_keys = OrderedDict()
        for k in keys:
            checked_keys[self.check_key(k)] = k
        cmd = name + b' ' + b' '.join(checked_keys) + b'\r\n'

        try:
            if not self.sock:
                self._connect()

            self.sock.sendall(cmd)

            buf = b''
            result = {}
            while True:
                buf, line = _readline(self.sock, buf)
                self._raise_errors(line, name)
                if line == b'END':
                    return result
                elif line.startswith(b'VALUE'):
                    if expect_cas:
                        _, key, flags, size, cas = line.split()
                    else:
                        try:
                            _, key, flags, size = line.split()
                        except Exception as e:
                            raise ValueError("Unable to parse line %s: %s"
                                                % (line, str(e)))

                    buf, value = _readvalue(self.sock, buf, int(size))
                    key = checked_keys[key]

                    if self.deserializer:
                        value = self.deserializer(key, value, int(flags))

                    if expect_cas:
                        result[key] = (value, cas)
                    else:
                        result[key] = value
                elif name == b'stats' and line.startswith(b'STAT'):
                    _, key, value = line.split()
                    result[key] = value
                else:
                    raise MemcacheUnknownError(line[:32])
        except Exception:
            self.close()
            if self.ignore_exc:
                return {}
            raise
