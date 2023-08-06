from __future__ import absolute_import
from __future__ import unicode_literals

import time
import uuid
import zlib
import struct
import collections
import logging
import os
import datetime
import os.path
import json

from six import text_type

import nacl.secret
import nacl.utils
import nacl.hash
import nacl.encoding


logger = logging.getLogger(__name__)


def json_default(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(repr(obj) + " is not JSON serializable")


class SessionExpired(Exception):
    pass


class InvalidSession(Exception):
    pass


class Session(collections.MutableMapping):
    """ A session acts like a dictionary to persist state between HTTP
    requests using cookies.

    The Session class have no knowledge of the storage layer and is used by
    SessionHandlers
    """
    # The format version is used to upgrade the encryption and serialization
    # algorithm
    id = None
    key = None
    _data = {}
    # fmt_version 1 was used for a AES-CTR + HMAC-SHA256 implementation using
    # the Python Cryptography library.
    fmt_version = 2
    expire_at = None
    ttl = None
    remote_ip = None
    is_modified = False
    is_new = False
    key_length = nacl.secret.SecretBox.KEY_SIZE

    def __init__(self, handler, session_id=None, key=None, remote_ip=None,
            data=None):
        """ Sessions are only initialized when they are actually used, to
        prevent needless session creation.
        """
        self.handler = handler
        self.remote_ip = remote_ip
        self.ttl = self.handler.ttl

        if session_id and key and data:
            assert isinstance(session_id, uuid.UUID), \
                    Exception('Session ID must be a UUID')
            assert isinstance(key, bytes), \
                    Exception('Key must be bytes, not %s' % type(key))
            assert len(key) == self.key_length, \
                    Exception('Key length must be %s' % len(key))
            self.id = session_id
            self.key = key
            self.decode(data, remote_ip=remote_ip)
            self.is_new = False
        elif not any((session_id, key, data)):
            # A new empty session
            self.is_new = True
        else:
            raise Exception('Existing sessions must specify key and data')

    def valid_mapping_key(self, key):
        if key.startswith('_'):
            raise Exception('Keys starting with an underscore are for '
                    'internal use only')
        return str(key)

    def __getitem__(self, key):
        key = self.valid_mapping_key(key)
        return self._data[key]

    def __setitem__(self, key, value):
        if not self.id:
            self._initialize()
        assert isinstance(key, text_type)
        key = self.valid_mapping_key(key)
        self._data[key] = value
        self.is_modified = True

    def __delitem__(self, key):
        key = self.valid_mapping_key(key)
        del self._data[key]
        self.is_modified = True

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def _enc_key(self):
        """ Construct encryption key by hashing the session specific key and
        a global secret key.
        """
        digest = nacl.hash.sha256(self.key + self.handler.secret_key,
                encoder=nacl.encoding.RawEncoder)
        assert len(digest) == nacl.secret.SecretBox.KEY_SIZE
        return digest

    def _initialize(self):
        """ Initializes the session as a new, fresh session which will be stored
        """
        # Python's uuid4 implementation uses system provided uuid library (such
        # as libuuid which uses /dev/urandom) or falls back to using
        # /dev/urandom directly. This seems to be sane behaviour.
        if self.id:
            self.reset()

        self.id = uuid.uuid4()
        self.key = nacl.utils.random(self.key_length)
        self._data = {}
        self.set_duration()
        self.is_modified = True
        self.is_new = True

    def reset(self):
        """ Reset session ID, key, data etc.
        """
        if self.id:
            self.id = None
            self.key = None
            self._data = {}
            self.is_modified = False

    def decode(self, data, remote_ip=None):
        """ Deserialize and check data into a valid session.
        Optionally check if remote_ip is identical to IP stored in session.
        """
        fmt_version = struct.unpack('<B', data[:1])[0]

        if fmt_version not in (2,):
            raise NotImplementedError('Session encoding format %d not supported',
                    fmt_version)


        # De-crypt
        box = nacl.secret.SecretBox(self._enc_key())
        try:
            data = box.decrypt(data[1:])
        except nacl.exceptions.BadSignatureError:
            raise InvalidSession('Session %s can\'t be authenticated, '
                    'will not decrypt' % self.id)
        except nacl.exceptions.CryptoError as e:
            raise InvalidSession('Session %s is invalid: %s' % (self.id, e))

        # Decompress
        data = zlib.decompress(data)

        # Deserialize JSON
        data = json.loads(data.decode('utf-8'))
        assert isinstance(data, dict), \
                Exception('Session must be a dictionary')

        self.expire_at = datetime.datetime.utcfromtimestamp(
                data.get('_expire_at', 0))
        self.remote_ip = data.get('_remote_ip')

        self.check(remote_ip=remote_ip)

        # Assign data only after checks are ok
        self._data = data

    def encode(self):
        self.set_duration()
        self._data['_expire_at'] = int(time.mktime(self.expire_at.timetuple()))
        self._data['_remote_ip'] = self.remote_ip

        data = json.dumps(self._data, default=json_default)

        data = zlib.compress(data.encode('utf-8'))

        # Encrypt data
        box = nacl.secret.SecretBox(self._enc_key())
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        encrypted = box.encrypt(data, nonce)
        return struct.pack('<B', self.fmt_version) + encrypted

    def set_duration(self, ttl=None):
        """ Set session duration
        """
        if ttl is not None:
            assert isinstance(ttl, datetime.datetime.timedelta)
            self.ttl = ttl

        self.expire_at = datetime.datetime.utcnow() + (self.ttl or self.handler.ttl)

    def has_expired(self):
        return self.expire_at < datetime.datetime.utcnow()

    def check(self, remote_ip=None):
        """ Check validity of session.
        """
        if self.has_expired():
            raise SessionExpired()

        if self.handler.ip_bound:
            if self.remote_ip is None:
                self.remote_ip = remote_ip
            elif remote_ip is None:
                raise InvalidSession('Remote IP unknown')
            elif self.remote_ip != remote_ip:
                raise InvalidSession('Remote IP changed')
