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
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Aerate(API):

    def __init__(self, spec_file=None,
                 middleware=None,
                 config=None):
        API.__init__(self, middleware=middleware)
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

    @staticmethod
    def load_spec(spec_file=None):

        if spec_file:
            swagger = Swagger()
            swagger.load_spec_from_file(spec_file)
        else:
            raise ValueError("spec_file must be provided")
        return swagger

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
                # Let's just add this route for now...
                self.add_route(
                    self._get_path_name_by_id(op_id),
                    res)
            else:
                raise ValueError('Error validating {0} in {1}'.format(
                    op_id, res.name()))
