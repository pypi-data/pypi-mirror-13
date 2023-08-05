# -*- coding: utf-8 -*-

import unittest
import aerate
import string
import random
import os
import simplejson as json
from datetime import datetime, timedelta
from aerate.tests.test_settings import MONGO_PASSWORD, MONGO_USERNAME, \
    MONGO_DBNAME, MONGO_HOST, MONGO_PORT

try:
    from urlparse import parse_qs, urlparse
except ImportError:
    from urllib.parse import parse_qs, urlparse


def close_pymongo_connection(app):
    """
    Close the pymongo connection in an eve/flask app
    """
    if 'pymongo' not in app.extensions:
        return
    del app.extensions['pymongo']
    del app.media
