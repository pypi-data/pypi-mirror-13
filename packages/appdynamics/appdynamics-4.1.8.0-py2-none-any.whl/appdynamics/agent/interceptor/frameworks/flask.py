# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for Flask framework.

"""

import sys

from appdynamics.agent.interceptor.frameworks.wsgi import WSGIInterceptor
from appdynamics.agent.interceptor.base import BaseInterceptor


class FlaskInterceptor(BaseInterceptor):
    def _handle_exception(self, handle_exception, flask, e):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                bt.add_exception(*sys.exc_info())

        return handle_exception(flask, e)


def intercept_flask(agent, mod):
    WSGIInterceptor(agent, mod.Flask).attach('wsgi_app')
    FlaskInterceptor(agent, mod.Flask).attach('handle_exception')
