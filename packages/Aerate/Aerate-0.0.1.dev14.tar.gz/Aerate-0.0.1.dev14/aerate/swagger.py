# -*- coding: utf-8 -*-
"""
    swagger
    ~~~~~~~~~~~~~~~
    Handles importation and validation of the Aerate swagger specification

    :copyright: (c) 2016 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.

"""
from bravado_core.spec import Spec
import json


class Swagger(object):

    def __init__(self, spec=None, config=None):
        self.spec_dict = None
        if spec:
            self.spec_dict = spec
        # TODO: Set defaults and read/set passed in config values.
        self.config = {
            'validate_requests': True,
            'validate_responses': True,
            'use_models': True,
        }
        if self.spec_dict:
            self.spec = Spec.from_dict(self.spec_dict, config=self.config)

    def _get_op_id_list(self):
        from itertools import chain
        op_id_list = []
        for res in self.spec.resources.keys():
            op_id_list.append(dir(self.spec.resources[res]))
        # Flatten down the list of operationIds:
        return list(chain.from_iterable(op_id_list))

    def _get_resource_list(self):
        return list(
            set([x.split('_')[0] for x in self._get_op_id_list()])
        )

    def _get_op_by_id(self, op_id):
        """
        Returns an bravado-core operation object correspoinding to a
        specific OperationId defined in the swagger spec.

        """
        op = None
        for resource in self.spec.resources.keys():
            op = getattr(self.spec.resources[resource], op_id)
            if op:
                return op
        return op

    def load_spec_from_file(self, filename):
        import os
        fileName, fileExtension = os.path.splitext(filename)
        if fileExtension == '.json':
            self.spec_dict = json.loads(open(filename, 'r').read())
        elif fileExtension == '.yaml':
            import yaml
            self.spec_dict = yaml.load(filename)
        else:
            raise TypeError("cannot detect filetype of {0}".format(filename))
        self.spec = Spec.from_dict(self.spec_dict, config=self.config)

    def load_spec_from_uri(self, uri):
        raise NotImplementedError()

    def spec(self):
        if self.spec:
            print self.spec
        else:
            print "No spec defined"
