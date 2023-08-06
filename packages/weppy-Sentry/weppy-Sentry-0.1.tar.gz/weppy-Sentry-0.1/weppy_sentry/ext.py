# -*- coding: utf-8 -*-
"""
    weppy_sentry.ext
    ----------------

    Provides sentry extension for weppy

    :copyright: (c) 2016 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import raven
import sys
from weppy._compat import iteritems
from weppy.extensions import Extension
from weppy.globals import current
from weppy.handlers import Handler


class Sentry(Extension):
    client = None
    default_config = dict(
        dsn='',
        auto_load=True
    )

    _errmsg = "You need to configure Sentry extension before using its methods"

    def _load_config(self):
        for key, value in self.default_config.items():
            self.config[key] = self.config.get(key, value)

    def on_load(self):
        self._load_config()
        self.handler = SentryHandler(self)
        if not self.config.dsn:
            return
        self.client = raven.Client(self.config.dsn)
        if self.config.auto_load:
            self.app.common_handlers.insert(0, self.handler)

    def _build_ctx_data(self):
        ctx = {'extra': {}}
        try:
            ctx['request'] = Serializer.serialize_request(current.request)
            ctx['extra']['response'] = \
                Serializer.serialize_response(current.response)
            ctx['extra']['session'] = \
                Serializer.serialize_session(current.session)
            ctx['user'] = Serializer.serialize_user(current.session)
        except:
            pass
        return ctx

    def exception(self, **kwargs):
        assert self.client, self._errmsg
        self.client.captureException(
            sys.exc_info(), data=self._build_ctx_data(), **kwargs)

    def message(self, msg, **kwargs):
        assert self.client, self._errmsg
        self.client.captureMessage(msg, data=self._build_ctx_data(), **kwargs)


class SentryHandler(Handler):
    def __init__(self, ext):
        self.ext = ext

    def on_failure(self):
        self.ext.exception()


class Serializer(object):
    @staticmethod
    def serialize_request(request):
        return {
            'url': "%s://%s%s" % (
                request.scheme, request.hostname, request.path_info),
            'method': request.method,
            'query_string': request.environ.get('QUERY_STRING', ''),
            'data': request.body_params,
            'env': request.environ
        }

    @staticmethod
    def serialize_response(response):
        rv = {
            'status': response.status,
            'headers': response.headers,
            'meta': response.meta,
            'meta_prop': response.meta_prop
        }
        if hasattr(response, 'output'):
            rv['output'] = response.output
        return rv

    @staticmethod
    def serialize_session(session):
        rv = {}
        if session:
            #: filter unsafe attributes from session
            filtered = ['_csrf', '_flashes', 'auth']
            for key, val in iteritems(session):
                if key in filtered:
                    continue
                rv[key] = val
            if isinstance(session.auth, dict):
                #: make a filtered version of auth attribute
                rv['auth'] = {}
                filtered_auth = ['user', 'hmac_key']
                for key, val in iteritems(session.auth):
                    if key in filtered_auth:
                        continue
                    rv['auth'][key] = val
        return rv

    @staticmethod
    def serialize_user(session):
        rv = {}
        if session and session.auth:
            if session.auth.user:
                #: try to fetch id and email from auth
                try:
                    rv['id'] = session.auth.user.id
                    rv['email'] = session.auth.user.email
                except:
                    pass
        return rv
