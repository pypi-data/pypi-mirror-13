from __future__ import unicode_literals

import pytest
import datetime

from pithos import BaseStore
from pithos import BaseSessionHandler


def test_handler():
    s = BaseStore()
    key = b'x' * 64
    h = BaseSessionHandler(s, key)

    assert h.store == s
    assert h.secret_key == key
    assert isinstance(h.ttl, datetime.timedelta)
    assert h.ttl.total_seconds() == 86400
    assert h.ip_bound == False


def test_custom_handler(handler_class):
    s = BaseStore()
    key = b'x' * 64
    h = handler_class(s, key, ttl=123456, ip_bound=True)
    assert h.ttl.total_seconds() == 123456
    assert h.ip_bound == True


def test_invalid_handler():
    s = BaseStore()
    with pytest.raises(AssertionError):
        BaseSessionHandler(s, 'x')

    with pytest.raises(AssertionError):
        BaseSessionHandler('y', 'x' * 64)

    with pytest.raises(AssertionError):
        BaseSessionHandler(s, 'x' * 64, ttl='2 days')

    with pytest.raises(AssertionError):
        BaseSessionHandler(s, 'x' * 64, ip_bound=1)

    with pytest.raises(AssertionError):
        BaseSessionHandler(s, 'x' * 64)
