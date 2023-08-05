# -*- coding: utf-8 -*-
"""
    aerate.collection_resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements a ResourceCollection for use in defining Falcon routes.
    The ResourceCollection must be subclassed in a user's application

    :copyright: (c) 2016 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.
"""


class ResourceCollection(object):

    def __init__(self):
        pass

    def on_get(**kwargs):
        pass

    def on_post(**kwargs):
        pass

    def on_put(**kwargs):
        pass

    def on_delete(**kwargs):
        pass

    def on_patch(**kwargs):
        pass
