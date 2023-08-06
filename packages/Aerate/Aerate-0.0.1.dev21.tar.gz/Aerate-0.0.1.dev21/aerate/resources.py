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

METHODS = ['on_get', 'on_post', 'on_put', 'on_delete', 'on_patch']
VERBS = ['get', 'put', 'post', 'delete', 'patch']
METHOD_ARGS = set(['req', 'resp'])


class Resource(object):

    def __init__(
            self,
            definition=None,
            datasource=None,
            id_field=None,
            authorization=None,
            schema=None,
            **kwargs):
        self.id_field = id_field or config.ID_FIELD
        self.schema = schema
        self.definition = definition
        for arg in kwargs.keys():
            setattr(self, arg, kwargs[arg])
        # Prevent user overloading of methods
        self.methods = []
        # Initialize with passed hanlder functions.
        # These functions must be of the form:
        #  f(self, req, resp, **kwargs)
        self.datasource = datasource
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

    # def on_get(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_post(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_put(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_delete(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_patch(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def _set_definition(self):
    #     return self.get_datasource().title()

    # def get_datasource(self):
    #     import re
    #     match = re.match('^.*(?=Item|Collection)', self.name())
    #     if match:
    #         return match.group(0).lower()
    #     else:
    #         return self.name().lower()

    def name(self):
        return self.__class__.__name__

    def valid_methods(self):
        return self._valid_methods(METHODS)

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
        if not METHOD_ARGS.intersection(args) == METHOD_ARGS:
            raise ValueError('method {0} in {1} requires args {2}'.format(
                method, self.name(), list(METHOD_ARGS)))
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


class ResourceItem(Resource):

    def __init__(self, **kwargs):
        super(ResourceItem, self).__init__(**kwargs)
        self.type = 'Item'


class MediaResourceCollection(ResourceCollection):

    def __init__(self, **kwargs):
        super(MediaResourceCollection, self).__init__(**kwargs)


class MediaResourceItem(ResourceItem):

    def __init__(self, **kwargs):
        super(MediaResourceItem, self).__init__(**kwargs)
