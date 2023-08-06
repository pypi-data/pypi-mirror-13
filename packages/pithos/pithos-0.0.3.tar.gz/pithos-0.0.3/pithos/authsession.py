from __future__ import unicode_literals
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)


def get_user_id(session):
    """ Retrieve user id from session instance
    """
    try:
        return session['user']['id']
    except KeyError:
        return None


def get_user_extra(session):
    """ Retrieve extra user session details from session instance
    """
    try:
        return session['user']['extra']
    except KeyError:
        return {}


def get_user_checkvalue(session):
    try:
        return session['user']['checkvalue']
    except KeyError:
        return None


def login(session, user_id, checkvalue, **kwargs):
    """ Login the user on the session instance.

    Starts a fresh session to avoid session fixation.

    The check value must be provided. The value should be changed to invalidate
    all sessions for the user, for example when a user updates its password or
    suspects unauthorized access to its account. It could be a hash of the
    users password hash or a serial number which increases on every change.

    Extra keyword arguments can be used to store extra information with
    the user ID on the session, such as the used authentication backend.

    Make sure all values are JSON serializable.
    """
    session.reset()
    logger.info('Login user %s on session %s', user_id, session.id)
    session['user'] = {'id': user_id, 'checkvalue': checkvalue, 'extra': kwargs}


def logout(session, response=None):
    """ Logout account and delete the session

    When a response is provided it will also try to empty and expire the session
    cookie.
    """
    logger.info('Logout session %s, user %d', session.id, get_user_id(session))
    session.handler.delete_session(session, response)


def keep_login(session, user_id, checkvalue):
    """ Call this after a password change or other action which changes the
    accounts session 'checkvalue'.
    """
    if get_user_id(session) == user_id:
        logger.info('Keep login for user %s session %s', user_id, session.id)
        session['user']['checkvalue'] = checkvalue
    else:
        logger.error('One can only update the checkvalue on an authenticated '
                'session when the user ID still matches.')
        logout(session)


def check_session(session, checkvalue, response=None):
    """ Retrieve user ID and check its checkvalue

    This must be called on EVERY incoming HTTP request with an authenticated
    session.
    """
    sess_check_value = get_user_checkvalue(session)

    if sess_check_value != checkvalue:
        user_id = get_user_id(session)
        logger.info('Session %s user %s: check value mismatch',
                session.id, user_id)
        logout(session, response)
        return False
    else:
        return True
