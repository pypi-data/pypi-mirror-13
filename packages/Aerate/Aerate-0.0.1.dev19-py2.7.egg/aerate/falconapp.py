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
from swagger import Swagger
from aerate.auth import Auth
from aerate.middleware import OpMiddleware
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Aerate(API):

    def __init__(self, spec_file=None,
                 auth=None,
                 middleware=None,
                 config=None):
        #create middleware for consumes/produces validation
        # middleware = self.createMiddleware(middleware)

        API.__init__(self, middleware=middleware)
        if not self._before:
            self._before = []
        self.auth_dict = {}
        if auth:
            for auth_obj in auth:
                self.auth_dict[auth_obj.__class__.__name__] = auth_obj
        self.resource_list = []
        self.op_dict = {}
        self.swagger = self.load_spec(spec_file=spec_file)
        # Put the base path into the app object for easy retrieval
        if 'basePath' in self.swagger.spec_dict:
            self.base_path = self.swagger.spec_dict['basePath']
        else:
            self.base_path = None
        # Put the API URL into the app object for easy retrieval
        self.api_url = self.swagger.spec.api_url
        # Make a single master list of all the OperationIds in the spec:
        self.op_ids_in_spec = self.swagger._get_op_id_list()
        # Make a single master list of all the Resources in the spec:
        self.resource_list = self.swagger._get_resource_list()


    # def createMiddleware(self, middleware=None):
    #     self._opMiddleware = OpMiddleware()
    #     if middleware:
    #         middleware.insert(0, self._opMiddleware )
    #     else:
    #         middleware = [ self._opMiddleware  ]
    #     return middleware

    @staticmethod
    def load_spec(spec_file=None):

        if spec_file:
            swagger = Swagger()
            swagger.load_spec_from_file(spec_file)
        else:
            raise ValueError("spec_file must be provided")
        return swagger

    def _add_auths_to_route(self, auths=[]):
        if auths:
            self._before.insert(0, Auth.last)
            [self._before.insert(0, auth) for auth in auths]
            self._before.insert(0, Auth.first)

    def _remove_auths_from_global(self, auths=[]):
        if self._before and auths:
            [auths.append(x) for x in [Auth.last, Auth.first]]
            # Find any instances of auths on self._before and get rid of them:
            [self._before.remove(obj) for obj in auths]

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
            return self.base_path + self.op_dict[op_id].path_name
        except KeyError:
            raise('{0} not found in list of OperationIds'.format(op_id))

    def add_resource(self, res):
        if res.name() not in self.resource_list:
            raise ValueError("{0} not in {1}".format(
                res.name(),
                self.resource_list))
        # Check to make sure defined methods match the OperationIds
        # for this resource:
        for op_id in res.valid_operationIds():
            # Grab the correct swagger operation based on this op_id
            op = self.swagger._get_op_by_id(op_id)
            # Only add this route if the route function passes validation:
            if res._validate_function_args(op):
                self.op_dict[op_id] = op
                #add operation to validation middleware
                # self._opMiddleware.addOp(op_id, op)
                # Let's just add this route for now...
                self._add_route_with_auth(op_id, res)
            else:
                raise ValueError('Error validating {0} in {1}'.format(
                    op_id, res.name()))

    def _add_route_with_auth(self, op_id , res):
        # jump in here and alter self._before to include auths:
        auths = self.swagger._get_security(op_id)
        if auths:
            auth_funs = []
            [auth_funs.append(self.auth_dict[auth]) for auth in auths]
            self._add_auths_to_route(auth_funs)
        self.add_route(
            self._get_path_name_by_id(op_id),
            res)
        if auths:
            # After adding this route, we remove the auth list from the
            # global auth list.
            self._remove_auths_from_global(auth_funs)