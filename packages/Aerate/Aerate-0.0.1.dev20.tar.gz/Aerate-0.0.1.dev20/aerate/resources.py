# -*- coding: utf-8 -*-
"""
    aerate.resources
    ~~~~~~~~~~~~~~~~
    Implements ResourceCollection and ResourceItem for use in
    defining Falcon routes.

    The ResourceItem must be subclassed in a user's application

    :copyright: (c) 2016 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.
"""
from aerate.config import config

methods = ['on_get', 'on_post', 'on_put', 'on_delete', 'on_patch']
verbs = ['get', 'put', 'post', 'delete', 'patch']
method_args = set(['req', 'resp'])


class Resource(object):

    def __init__(
            self,
            id_field=None,
            datasource=None,
            authorization=None,
            definition=None,
            schema=None):
        self.id_field = id_field or config.ID_FIELD
        self.datasource = datasource or self.get_datasource()
        self.definition = definition or self._set_definition()
        self.schema = schema or None
        self.methods = []
        # Initialize with passed hanlder functions.
        # These functions must be of the form:
        #  f(self, req, resp, **kwargs)
        if datasource:
            self.datasource = datasource
        if authorization:
            self.authorize = authorization

    def authorize(self, req, resp, **kwargs):
        """ Authorizes access to items for this resource. Authorization
        is designed to use an item field to determine item-level access,
        but any other scheme could be implemented. Authorization does not
        replace authentication. Authenthication should only confirm user
        identity and claims, not user access to resources or actions.
        """
        raise NotImplementedError

    def filter(self, req, resp, **kwargs):
        """ Filters response objects based on spec-level flags.
        Filter works in a similar fashion as validate; checking object
        fields to confirm that they are defined in the spec, and that
        they are not marked private (x-aerate-private) in the spec before
        returning response objects.
        """
        pass

    def _set_definition(self):
        return self.get_datasource().title()

    def get_datasource(self):
        import re
        match = re.match('^.*(?=Item|Collection)', self.name())
        if match:
            return match.group(0).lower()
        else:
            return self.name().lower()

    def name(self):
        return self.__class__.__name__

    def valid_methods(self):
        return self._valid_methods(methods)

    def valid_operationIds(self):
        return list(
            [str(self.name() + '_' + method) for
                method in self.valid_methods()]
        )

    def get_before_method(self, op_id):
        return getattr(self, "before_on_" + op_id, None)

    def get_after_method(self, op_id):
        return getattr(self, "after_on_" + op_id, None)

    def get_authorize_method(self, op_id):
        return getattr(self, "authorize_on_" + op_id, None)

    def _valid_methods(self, m):
        valid = []
        for method in m:
            if getattr(self, method, None):
                valid.append(method)
        return valid

    def _validate_function_args(self, op):
        if not op:
            raise ValueError(
                'No operation to validate {0}'.format(self.name()))
        from inspect import getargspec
        method = "on_" + op.http_method
        fun = getattr(self, method, None)
        if not fun:
            raise ValueError('method {0} in {1} not defined'.format(
                method, self.name()))
        args = set(getargspec(fun).args)
        if not method_args.intersection(args) == method_args:
            raise ValueError('method {0} in {1} requires args {2}'.format(
                method, self.name(), list(method_args)))
        # Check to see if each param for this operation is required:
        for p in op.params.keys():
            spec = op.params[p].param_spec
            if spec['in'] == 'path' and spec['required']:
                if p not in list(args):
                    raise ValueError(
                        'method {0} in {1} requires arg {2}'.format(
                            method, self.name(), p))
        return True


class ResourceCollection(Resource):

    def __init__(self, **kwargs):
        super(ResourceCollection, self).__init__(**kwargs)
        self.type = 'Collection'

    # def on_get(self, req, resp, **kwargs):
    #    if self.is_allowed('GET'):
    #        db.find(req, resp, **kwargs)

    # def on_post(self, **kwargs):
    #    if self.is_allowed('POST'):
    #        db.create(req, resp, **kwargs)

    # def on_put(self, **kwargs):
    #     pass

    # def on_delete(self, **kwargs):
    #     pass

    # def on_patch(self, **kwargs):
    #     pass


class ResourceItem(Resource):

    def __init__(self, **kwargs):
        super(ResourceItem, self).__init__(**kwargs)
        self.type = 'Item'

    # def on_get(self, **kwargs):
    #    if self.is_allowed('GET'):
    #        db.find_one(req, resp, **kwargs)

    # def on_post(self, **kwargs):
    #     if self.is_allowed('POST'):
    #        db.find_one(req, resp, **kwargs)

    # def on_post(self, **kwargs):
    #     pass

    # def on_put(self, **kwargs):
    #     pass

    # def on_delete(self, **kwargs):
    #     pass

    # def on_patch(self, **kwargs):
    #     pass
