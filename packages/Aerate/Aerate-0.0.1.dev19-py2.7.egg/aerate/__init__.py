# -*- coding: utf-8 -*-

"""
    Aerate
    ~~~
    A REST Web API that has falcon swagger.
    :copyright: (c) 2015 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.

"""

__version__ = '0.0.1.dev19'

from aerate.swagger import Swagger
from aerate.resources import ResourceCollection, ResourceItem

# This should be at the end of the file
from aerate.falconapp import Aerate
