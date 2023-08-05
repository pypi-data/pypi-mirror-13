
class BaseStore(object):
    """Base class for session stores"""
    def bind(self, handler):
        self.handler = handler

    def load(self, session_id):
        raise NotImplementedError()

    def save(self, session):
        raise NotImplementedError()

    def delete(self, session_id):
        raise NotImplementedError()

    def cleanup(self, ttl):
        """removes all expired sessions"""
        return NotImplemented
