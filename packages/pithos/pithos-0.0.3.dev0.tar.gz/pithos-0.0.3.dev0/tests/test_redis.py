from __future__ import unicode_literals
from __future__ import absolute_import

from pithos.redis import RedisStore


def test_disk(request_class, handler_class):
    store = RedisStore('pithos-test')
    r = request_class()
    h = handler_class(store, secret_key=b'x' * 64)
    s = h.get_session(r)
    assert s.is_modified == False
    s['test'] = u'A very good morning'
    assert s.is_modified == True

    encoded = s.encode()
    s.decode(encoded, s.remote_ip)

    h.save_session(s, r)

    assert isinstance(h.store, RedisStore)
    s2 = h.get_session(r)
    assert s2.is_modified == False
