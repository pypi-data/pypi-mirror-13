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

    def __init__(self, spec_file=None, config=None):
        if spec_file:
            self.spec_dict = json.loads(open(spec_file, 'r').read())
        else:
            raise ValueError("spec_file must be provided")
        # TODO: Set defaults and read/set passed in config values.
        self.config = {
            'validate_requests': True,
            'validate_responses': True,
            'use_models': True,
        }
        self.spec = Spec.from_dict(self.spec_dict, config=self.config)
