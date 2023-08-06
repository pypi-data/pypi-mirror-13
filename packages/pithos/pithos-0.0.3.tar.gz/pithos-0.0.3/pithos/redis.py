from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import redis

from pithos.store import BaseStore

logger = logging.getLogger(__name__)


class RedisStore(BaseStore):
    def __init__(self, prefix='pithos', connection_pool=None,
            **conn_kwargs):
        """ The `prefix` is used to prefix session ID's, use a custom
        prefix to clearly seperate sessions for seperate projects.

        Either specify connection keyword arguments which will be passed to
        `redis.connection.ConnectionPool` or an already configured
        connection_pool.
        """
        self.prefix = prefix

        if connection_pool and conn_kwargs:
            raise Exception('Either specify connection keyword arguments or '
                    'an already configured Redis connection pool')

        elif not connection_pool:
            connection_pool = redis.connection.ConnectionPool(**conn_kwargs)

        self.r_client = redis.StrictRedis(connection_pool=connection_pool)
        # Test connection with Redis:
        self.r_client.ping()

    def _key(self, session_id):
        return self.prefix + u':' + str(session_id)

    def load(self, session_id):
        return self.r_client.get(self._key(session_id))

    def save(self, session):
        if not session.id:
            return
        data = session.encode()
        ttl = int(session.ttl.total_seconds())
        self.r_client.setex(self._key(session.id), ttl, data)

    def delete(self, session_id):
        self.r_client.delete(self._key(session_id))

    def cleanup(self, ttl):
        # This method is a NO-OP, Redis expires sessions automatically
        pass
