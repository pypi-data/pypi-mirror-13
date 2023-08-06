from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import logging
import base64
import uuid
import re

from six import text_type

from pithos.session import Session
from pithos.store import BaseStore


logger = logging.getLogger(__name__)


class CookieError(Exception):
    pass


class BaseSessionHandler(object):
    """ Top level session handling object. Most applications only need one
    session handler. Frameworks may inherit this handler and implement web
    framework specifics.
    """
    session_class = Session

    # Session cookie consists of two base64 encoded strings, the first is
    # 16 octets and the second 32 octets, seperated by a colon.
    # Base64 encoded length is thus 24 + 1 + 44 = 69
    re_cookie_value = re.compile('^[A-Za-z0-9\-_]{22}==:[A-Za-z0-9\-_]{43}=$')
    cookie_value_len = 69

    def __init__(self,
            store,
            secret_key,
            cookie_name='session_id',
            cookie_domain=None,
            cookie_path=None,
            cookie_httponly=True,
            cookie_secure=True,
            ttl=86400,
            permanent=True,
            ip_bound=False):
        """ Configure session management

        ``store`` is a websession storage instance.

        The ``secret_key`` is a byte string used together with the session
        specific key to compose the sessions' encryption key. Changing the
        secret key immediatly invalidates all sessions.

        ``ttl`` is session expiry period in seconds. This must be set, even
        when sessions are not permanent.

        ``permanent`` permanent session are kept between browser restarts while
        non permanent session are removed by browsers.

        Individual sessions may set specific ttl's and may deviate from the
        handlers `permanent` setting.

        ``ip_bound`` determines if the session must be bound to one IP address.
        This increases security but might cause problems for users which
        legitimately switch address during a session.
        """
        assert isinstance(store, BaseStore)
        self.store = store
        self.store.bind(self)

        assert isinstance(secret_key, bytes), \
                Exception('Secret key must be bytes')
        assert len(secret_key) > 63, \
                Exception('Secret key must be at least 64 bytes')
        self.secret_key = secret_key

        assert isinstance(ttl, int), \
                Exception('Session TTL must be set an integer')
        ttl = datetime.timedelta(seconds=ttl)
        self.ttl = ttl

        assert isinstance(permanent, bool), \
                Exception('permanent must be a boolean')
        self.permanent = permanent

        assert isinstance(ip_bound, bool), \
                Exception('ip_bound must be a boolean')
        self.ip_bound = ip_bound

        self.cookie_name = cookie_name
        self.cookie_domain = cookie_domain
        self.cookie_path = cookie_path
        self.cookie_httponly = cookie_httponly
        self.cookie_secure = cookie_secure

    def get_session(self, request):
        session = None
        value = self.get_cookie(request)
        # FIXME validate remote IP, treat as 'user input',
        remote_ip = self.get_remote_ip(request)

        if value is not None:
            assert isinstance(value, text_type)
            if (len(value) == self.cookie_value_len and
                    self.re_cookie_value.match(value)):
                try:
                    sid, key = value.encode('ascii').split(b':', 1)
                    sid = base64.urlsafe_b64decode(sid)
                    sid = uuid.UUID(bytes=sid)
                    key = base64.urlsafe_b64decode(key)
                except (ValueError, TypeError):
                    logger.debug('Invalid cookie value could not be parsed')
                else:
                    logger.debug('Loading session %s', sid)
                    data = self.store.load(sid)
                    if data:
                        session = self.session_class(handler=self, session_id=sid,
                                key=key, remote_ip=remote_ip, data=data)
                        logger.debug('Session %s loaded', sid)
            else:
                logger.debug('Invalid session cookie value')

        if session is None:
            session = self.session_class(handler=self, remote_ip=remote_ip)

        return session

    def save_session(self, session, response, enforce=False):
        if (session.id and session.is_modified) or enforce:
            logger.debug('Saving session %s, modified %s', session.id,
                    session.is_modified)
            cookie_value = (base64.urlsafe_b64encode(session.id.bytes) + b':' +
                    base64.urlsafe_b64encode(session.key))
            self.set_cookie(response, cookie_value.decode('ascii'))
            self.store.save(session)

    def delete_session(self, session, response=None):
        if session.id:
            self.store.delete(session.id)
            session.reset()

        if response is not None:
            self.del_cookie(response)

    def cleanup(self, ttl=None):
        """ Erase all expired sessions (when store type supports this)
        """
        self.store.cleanup(ttl or self.ttl.total_seconds())

    def get_cookie(self, request):
        """ Get session cookie from HTTP request instance.

        Must be implemented by handlers

        Must return the cookie value as a (text) string of the session cookie
        or None.
        """
        raise NotImplementedError()

    def set_cookie(self, response, value):
        """ Set session cookie on HTTP response instance to 'value'.

        Must be implemented by handlers

        Must set the session cookie to text string 'value'. When the response
        object requires binary values for cookies one may encode the 'value'
        using either ASCII or UTF-8.
        """
        raise NotImplementedError()

    def del_cookie(self, response):
        """ Remove session cookie from response instance.

        Cookie may not exist when this is called.

        Must be implemented by handlers
        """
        raise NotImplementedError()

    def get_remote_ip(self, request):
        """ Retrieve the remove ip address from a request instance.

        Must be implemented by handlers.
        """
        raise NotImplementedError()
