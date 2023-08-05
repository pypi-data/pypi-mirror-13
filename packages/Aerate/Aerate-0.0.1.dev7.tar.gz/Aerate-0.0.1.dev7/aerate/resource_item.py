# -*- coding: utf-8 -*-
"""
    aerate.resource_item
    ~~~~~~~~~~~~~~~~~~~~
    Implements a ResourceItem for use in defining Falcon routes.
    The ResourceItem must be subclassed in a user's application

    :copyright: (c) 2016 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.
"""


class ResourceItem(object):

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