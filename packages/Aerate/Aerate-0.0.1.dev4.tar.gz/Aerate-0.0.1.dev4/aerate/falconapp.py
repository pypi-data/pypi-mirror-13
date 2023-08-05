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
from serve_swagger import SpecServer


class Aerate(API):

    def __init__(self, middleware=None,
                 operation_handlers=None,
                 spec_file=None,
                 config=None):
        API.__init__(self, middleware=middleware)

        # TODO: add routes based on the swagger spec instead of a sink.
        # TODO: would prefer to use a more robust swagger parsing/validation;
        #       possibly bravado-core by Yelp.
        server = SpecServer(operation_handlers=operation_handlers)
        with open(spec_file) as f:
            server.load_spec_swagger(f.read())

        # Main API routes are created as a sink.
        self.add_sink(server, r'/')
