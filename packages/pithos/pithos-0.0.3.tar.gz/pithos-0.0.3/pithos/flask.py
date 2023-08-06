from __future__ import unicode_literals
from __future__ import absolute_import

import datetime

from six import binary_type

from pithos.handler import BaseSessionHandler
from pithos.session import Session

from flask.sessions import SessionMixin, SessionInterface


class FlaskSession(Session, SessionMixin):
    """ Session class which plays nicely with Flask
    """
    @property
    def new(self):
        return self.is_new

    @property
    def modified(self):
        return self.is_modified


class FlaskSessionHandler(BaseSessionHandler):
    session_class = FlaskSession

    def __init__(self, store, flask_app):
        self.flask_app = flask_app

        ttl = flask_app.config['PERMANENT_SESSION_LIFETIME']
        if isinstance(ttl, datetime.timedelta):
            ttl = int(ttl.total_seconds())

        key = flask_app.config['SECRET_KEY']
        if not isinstance(key, binary_type):
            key = key.encode('utf-8')

        super(FlaskSessionHandler, self).__init__(
            store,
            key,
            cookie_name=flask_app.config['SESSION_COOKIE_NAME'],
            cookie_domain=flask_app.config['SESSION_COOKIE_DOMAIN'],
            cookie_path=flask_app.config['SESSION_COOKIE_PATH'],
            cookie_httponly=flask_app.config['SESSION_COOKIE_HTTPONLY'],
            cookie_secure=flask_app.config['SESSION_COOKIE_SECURE'],
            ttl=ttl,
            ip_bound=flask_app.config.get('SESSION_IP_BOUND', False)
        )

    def get_cookie(self, request):
        return request.cookies.get(self.cookie_name) or None

    def set_cookie(self, response, value):
        return response.set_cookie(self.cookie_name, value, max_age=self.ttl,
                domain=self.cookie_domain, path=self.cookie_path or '/',
                secure=self.cookie_secure, httponly=self.cookie_httponly)

    def del_cookie(self, response):
        return response.set_cookie(self.cookie_name, '', max_age=0,
                domain=self.cookie_domain, path=self.cookie_path or '/',
                secure=self.cookie_secure, httponly=self.cookie_httponly)

    def get_remote_ip(self, request):
        return request.remote_addr


class FlaskSessionInterface(SessionInterface):
    def open_session(self, app, request):
        return app.pithos_handler.get_session(request)

    def save_session(self, app, session, response):
        return app.pithos_handler.save_session(session, response)


def setup_pithos(app, store):
    handler = FlaskSessionHandler(store, app)
    app.pithos_handler = handler
    app.session_interface = FlaskSessionInterface()
