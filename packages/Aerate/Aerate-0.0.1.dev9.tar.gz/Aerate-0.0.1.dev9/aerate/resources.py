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


class Resource(object):

    def __init__(self):
        pass

    def valid_methods(self):
        valid = []
        for method in methods:
            if getattr(self, method, None):
                valid.append(method)
        return valid

    def valid_operationIds(self):
        return list(
            [str(self.__class__.__name__ + '_' + method) for
                method in self.valid_methods()]
        )


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
