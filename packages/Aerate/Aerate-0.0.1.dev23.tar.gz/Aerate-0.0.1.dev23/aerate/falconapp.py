# -*- coding: utf-8 -*-
"""
    aerate.falconapp
    ~~~~~~~~~~~~~~~~
    This module implements the central WSGI application object as a Falcon
    subclass.
    :copyright: (c) 2016 by Arable Labs, Inc.
    :license: BSD, see LICENSE for more details.
"""
from falcon import API
from falcon import Request, Response
from aerate.swagger import Swagger
from aerate.io.mongo import Mongo
# from aerate.middleware import OpMiddleware
from aerate.config import config as app_config
from collections import deque
from aerate.validate import Validate
from aerate.middleware import AerateMiddleware

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Aerate(API):

    def __init__(
            self,
            spec_file=None,
            auth=None,
            middleware=None,
            data=Mongo,
            config=None,
            request_type=Request,
            response_type=Response,
            router=None):
            # create middleware for consumes/produces validation
        # middleware = self.createMiddleware(middleware)
        self.aerate_middleware = AerateMiddleware()
        if middleware:
            middleware.insert(0, self.aerate_middleware)
        else:
            middleware = [self.aerate_middleware]
        API.__init__(
            self,
            middleware=middleware,
            request_type=request_type,
            response_type=response_type,
            router=router)

        # Right now, the order of these matter. In particular, we cannot try
        # to initialize the data layer before we have the config done.

        # 1. Initialize the list of responder decorators. Cast a deque
        if not self._before:
            self._before = deque([])
        else:
            self._before = deque(self._before)

        if not self._after:
            self._after = []

        # 2. Initialize the auth dictionary:
        self.auth(auth)

        # 3. Specify the swagger spec:
        self.swagger = self.load_spec(spec_file=spec_file)
        self.spec_dict = self.swagger.spec.spec_dict

        # 3b. Setup resource information for this API
        # Should be an ImmutableDict or array of Tuples?
        # This resource map will contain:
        """
        ['definition':
            {'operations': [
                'op_id': {
                    'op': op_function
                    'authenticate': [authenticate],
                    'validate': [validate]
                    'on_before' on_before,
                    'on_after': on_after
                }
            ]
             'definition': definition,
             'schema': schema,
             'methods': methods
            }
        ]
        """
        self.resource_map = self.build_resource_map()

        # 4. Setup the API config settings:
        self.config(config)
        if data:
            # 5. Setup the datalayer connection:
            self.data = data()

        # 6. Initialize the operation dictionary
        self.op_dict = {}

    def build_resource_map(self):
        _map = []
        return _map

    def auth(self, auth=None):
        self.auth_dict = {}
        if auth:
            for auth_obj in auth:
                self.auth_dict[auth_obj.__class__.__name__] = auth_obj

    def config(self, config=None):
        """
        Sets the default config object using default_settings. Then tries to
        update default config object in aerate.config with app-specific and
        swagger-specific settings. These settings over-ride the defaults
        specified in aerate.__init__. The resulting config object can be
        used anywhere in the code, using 'from aerate.config import config'
        or from 'aerate.config import *'
        """
        import aerate.default_settings
        app_config.from_object(aerate.default_settings)
        if config:
            for key in config.keys():
                app_config.key = config[key]
        # Set some config based on swagger. A bit hacky.
        # Would be better to have a list of swagger configs and iterate?
        # TODO: Remove references to 'self' in code, and use 'config' instead.
        if self.swagger.spec.api_url:
            app_config.set('API_URL', self.swagger.spec.api_url)
        app_config.set('RESOURCES', self.swagger._get_resource_list())
        if 'basePath' in self.swagger.spec_dict:
            app_config.set('BASE_PATH', self.swagger.spec_dict['basePath'])

    @staticmethod
    def load_spec(spec_file=None):

        if spec_file:
            swagger = Swagger()
            swagger.load_spec_from_file(spec_file)
        else:
            raise ValueError("spec_file must be provided")
        return swagger

    def _add_auths_to_route(self, key, auths=[]):
        auth_funs=[]
        [auth_funs.append(self.auth_dict[auth]) for auth in auths]
        self.aerate_middleware.add_auths(key, auth_funs)

    def _get_method_by_id(self, op_id):
        """
        Returns an API HTTP method correspoding to an OperationId defined
        defined in the swagger spec
        """
        try:
            return self.op_dict[op_id].http_method
        except KeyError:
            raise('{0} not found in list of OperationIds'.format(op_id))

    def _get_path_name_by_id(self, op_id):
        """
        Returns an API path correspoding to an OperationId
        defined in the swagger spec. Includes base_path, if any
        """
        try:
            return app_config.BASE_PATH + self.op_dict[op_id].path_name
        except KeyError:
            raise('{0} not found in list of OperationIds'.format(op_id))

    def add_resource(self, res):
        if res.name() not in app_config.RESOURCES:
            raise ValueError("{0} not in {1}".format(
                res.name(),
                app_config.RESOURCES))
        # Check to make sure defined methods match the OperationIds
        # for this resource:
        for op_id in res.valid_operationIds():
            # Grab the correct swagger operation based on this op_id
            op = self.swagger._get_op_by_id(op_id)
            # Only add this route if the route function passes validation:
            if res._validate_function_args(op):
                self.op_dict[op_id] = op
                res.methods.append(op.http_method.upper())
                if op.http_method.upper() in ['POST', 'PUT', 'PATCH'] and \
                        not res.schema:
                    # Add the schema to the resource for request validation
                    try:
                        res.schema = self.spec_dict[
                            'definitions'][res.definition]
                    except KeyError:
                        raise KeyError(
                            'resource definition {0} not valid for {1}'.format(
                                res.definition, res.name()))
                # Let's just add this route for now...
                self._add_route_with_auth(op_id, res)
            else:
                raise ValueError('Error validating {0} in {1}'.format(
                    op_id, res.name()))

    def _add_route_with_auth(self, op_id, res):
        auths = self.swagger._get_security(op_id)
        self._add_auths_to_route(op_id, auths)
        self.add_route(self._get_path_name_by_id(op_id), res)
