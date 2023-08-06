# -*- coding: utf-8 -*-

"""
    Aerate
    ~~~
    A REST Web API that has falcon swagger.
    :copyright: (c) 2015 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.

"""
# flake8: noqa

__version__ = '0.0.1.dev20'

from aerate.swagger import Swagger
from aerate.resources import ResourceCollection, ResourceItem

# This should be at the end of the file
from aerate.falconapp import Aerate


# RFC 1123 (ex RFC 822)
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

API_URL = None
BASE_PATH = None
RESOURCES = None

# DEFINE META VARIABLES FOR CREATION/UPDATES:
CREATED = 'created'
UPDATED = 'updated'
ID_FIELD = '_id'
