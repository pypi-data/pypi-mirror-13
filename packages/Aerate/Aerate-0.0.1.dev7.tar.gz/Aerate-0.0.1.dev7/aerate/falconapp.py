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
# from serve_swagger import SpecServer
from swagger import Swagger


class Aerate(API):

    def __init__(self, middleware=None,
                 operation_handlers=None,
                 spec_file=None,
                 config=None):
        API.__init__(self, middleware=middleware)
        self.resources = {}
        self.operations = {}
        # use Swagger object to build a swagger spec object.
        if spec_file:
            self.swagger = Swagger()
            self.swagger.load_spec_from_file(spec_file)
        else:
            raise ValueError("spec_file must be provided")

        for resource in self.swagger.spec.resources:
            self.add_resource(resource)

        # TODO: add routes based on the swagger spec instead of a sink.
        # TODO: would prefer to use a more robust swagger parsing/validation;
        #       possibly bravado-core by Yelp.
        # server = SpecServer(operation_handlers=operation_handlers)
        # with open(spec_file) as f:
        #     server.load_spec_swagger(f.read())

        # Main API routes are created as a sink.
        # self.add_sink(server, r'/')

    def add_resource(self, resource):
        res = resource.__class__.__name__
        for method in ['on_get', 'on_post', 'on_delete', 'on_put']:
            op = getattr(resource, method, None)
            if op:
                op_id = res + '_' + method
                self.operations[op_id] = op
