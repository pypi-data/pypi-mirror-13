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
methods = ['on_get', 'on_post', 'on_put', 'on_delete', 'on_patch']
method_args = set(['req', 'resp'])


class Resource(object):

    def __init__(self):
        pass

    def name(self):
        return self.__class__.__name__

    def valid_methods(self):
        valid = []
        for method in methods:
            if getattr(self, method, None):
                valid.append(method)
        return valid

    def valid_operationIds(self):
        return list(
            [str(self.name() + '_' + method) for
                method in self.valid_methods()]
        )

    def _validate_function_args(self, op):
        if not op:
            raise ValueError('No operation to validate {0}'.format(self.name()) )
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

    def __init__(self):  # , name, resource):
        self.type = 'Collection'

    # def on_get(self, **kwargs):
    #     pass

    # def on_post(self, **kwargs):
    #     pass

    # def on_put(self, **kwargs):
    #     pass

    # def on_delete(self, **kwargs):
    #     pass

    # def on_patch(self, **kwargs):
    #     pass


class ResourceItem(Resource):

    def __init__(self):
        self.type = 'Item'

    # def on_get(self, **kwargs):
    #     pass

    # def on_post(self, **kwargs):
    #     pass

    # def on_put(self, **kwargs):
    #     pass

    # def on_delete(self, **kwargs):
    #     pass

    # def on_patch(self, **kwargs):
    #     pass
