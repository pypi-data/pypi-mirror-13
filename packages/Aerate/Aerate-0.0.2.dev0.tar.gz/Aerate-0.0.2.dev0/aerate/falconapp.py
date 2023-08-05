# -*- coding: utf-8 -*-
"""
    aerate.falconapp
    ~~~~~~~~~~~~~~~~
    This module implements the central WSGI application object as a Falcon
    subclass.
    :copyright: (c) 2016 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.
"""
from falcon import API
import aerate


class Aerate(API):

    def __init__(self, middleware=None, config=None):
        API.__init__(self, middleware=middleware)
        self._set_defaults(self)
        if config:
            self._update_config(config)

    def _set_defaults(self):
        pass

    def _update_config(self, config):
        pass
