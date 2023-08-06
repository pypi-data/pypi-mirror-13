# -*- coding: utf-8 -*-

"""
    aerate.io.mongo.mongo (aerate.io.mongo)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    The actual implementation of the MongoDB data layer.
    :copyright: (c) Arable Labs, Inc.
    :license: BSD, see LabsICENSE for more details.

"""
from aerate.io.base import DataLayer, ConnectionException
from bson.objectid import ObjectId
from aerate.utils import str_to_date
import simplejson as json
import datetime
from pymongo import MongoClient
from aerate.config import config


class Mongo(DataLayer):
    """ MongoDB data access layer for Aerate REST API.

    """

    # Here are some default serializers we will need to use:
    serializers = {
        'objectid': lambda value: ObjectId(value) if value else None,
        'datetime': str_to_date,
        'integer': lambda value: int(value) if value is not None else None,
        'float': lambda value: float(value) if value is not None else None,
        'number': lambda val: json.loads(val) if val is not None else None
    }

    # Here's the set of mongodb operators that queries may be using:
    operators = set(
        ['$gt', '$gte', '$in', '$lt', '$lte', '$ne', '$nin'] +
        ['$or', '$and', '$not', '$nor'] +
        ['$mod', '$regex', '$text', '$where'] +
        ['$options', '$search', '$language'] +
        ['$exists', '$type'] +
        ['$geoWithin', '$geoIntersects', '$near', '$nearSphere'] +
        ['$all', '$elemMatch', '$size']
    )

    def init_driver(self):
        # mongod must be running or this will raise an exception
        self.driver = self.pymongo()
        self.mongo_prefix = None

    def retrieve_one_raw(self, res, _id):
        """ Retrieves a single raw document.
        :param res: resource object.
        :param _id: unique id.
        .. versionchanged:: 0.6
           Support for multiple databases.
        .. versionadded:: 0.4
        """
        document = self.pymongo()[res.datasource].find_one({res.id_field: _id})
        return document

    def retrieve_one(self, res, req, **lookup):
        """ Retrieves a single document.
        :param resource: resource name.
        :param req: a :class:`ParsedRequest` instance.
        :param **lookup: lookup query.
        """
        pass

    def create(self, res, obj):

        if config.CREATED:
            if type(obj) is dict:
                obj[config.CREATED] = datetime.datetime.now()
            elif type(obj) is list:
                for item in obj:
                    item[config.CREATED] = datetime.datetime.now()

        return self.pymongo()[res.datasource].insert(obj)

    def pymongo(self):
        """ Returns the PyMongo instance, which is stored in self.driver.
        In the future, we may need multiple instances, in which case, this
        function can be refactored to return the appropriate PyMongo
        instance depending on the resource, etc...
        """
        if not self.driver:
            try:
                # instantiate and add to cache
                self.driver = self.PyMongo()
            except Exception as e:
                raise ConnectionException(e)
            return self.driver
        return self.driver[config.MONGO_DBNAME]

    def PyMongo(self):
        return MongoClient(
            host=config.MONGO_HOST,
            port=config.MONGO_PORT
        )
