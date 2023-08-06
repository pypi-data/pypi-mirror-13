from __future__ import unicode_literals
from __future__ import absolute_import

from pithos.filesystem import FilesystemStore


def test_disk(request_class, handler_class, tmpdir):
    root = tmpdir.mkdir('test_disk').dirname
    store = FilesystemStore(root)
    r = request_class()
    h = handler_class(store, secret_key=b'x' * 64)
    s = h.get_session(r)
    assert s.is_modified == False
    s['test'] = u'A very good morning'
    assert s.is_modified == True

    encoded = s.encode()
    s.decode(encoded, s.remote_ip)

    h.save_session(s, r)

    assert h.store.root == root

    assert isinstance(h.store, FilesystemStore)
    s2 = h.get_session(r)
    assert s2.is_modified == False


def test_cleanup(handler_class, tmpdir):
    root = tmpdir.mkdir('cleanup').dirname
    store = FilesystemStore(root)
    handler_class(store, secret_key=b'x' * 64)
    store.cleanup(0)
