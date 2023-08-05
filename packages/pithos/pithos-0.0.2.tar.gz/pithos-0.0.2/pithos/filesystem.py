from __future__ import unicode_literals
from __future__ import absolute_import

import os
import time
import uuid
import logging

from pithos.store import BaseStore

logger = logging.getLogger(__name__)


class FilesystemStore(BaseStore):
    """ Store for saving a session on the filesystem.
    """
    def __init__(self, root):
        # if the storage root doesn't exists, create it.
        self.root = os.path.abspath(root)
        if not os.path.exists(self.root):
            logger.debug('Creating session storage dir %s', self.root)
            os.makedirs(self.root)

        # Test if directory is writable
        try:
            h = open(os.path.join(root, '.test'), 'w')
            h.write('test')
            h.close()
        except IOError:
            raise Exception('Session storage directory %s not writable' % root)
        finally:
            try:
                os.unlink(os.path.join(root, '.test'))
            except FileNotFoundError:
                pass

    def _get_path(self, session_id):
        assert isinstance(session_id, uuid.UUID), \
                Exception('Session ID must be a UUID')
        return os.path.join(self.root, str(session_id))

    def load(self, session_id):
        path = self._get_path(session_id)
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except IOError:
            logger.info('Could not load session %s', session_id)
        else:
            return data

    def save(self, session):
        if not session.id:
            return

        path = self._get_path(session.id)
        try:
            with open(path, 'wb') as f:
                f.write(session.encode())
        except IOError:
            logger.error('Could not store session %s', session.id)
            pass

    def delete(self, session_id):
        path = self._get_path(session_id)
        if os.path.exists(path):
            os.unlink(path)

    def cleanup(self, ttl):
        """ Call this regularly (e.g. in a CRON job) to recover storage used by
        expired sessions.  """
        now = time.time()
        for f in os.listdir(self.root):
            try:
                session_id = uuid.UUID(f)
            except ValueError:
                continue

            path = self._get_path(session_id)
            atime = os.stat(path).st_atime
            if now - atime > ttl:
                os.unlink(path)
