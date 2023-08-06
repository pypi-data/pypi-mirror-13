from aerate.tests import TestBase
from aerate.io.mongo import Mongo
from aerate.io import ConnectionException
from aerate.config import config
from aerate.resources import Resource
from pymongo import MongoClient
from bson import ObjectId


class TestDataLayer(TestBase):

    def setUp(self):
        super(TestDataLayer, self).setUp()
        self.pymongo = MongoClient()

    def tearDown(self):
        super(TestDataLayer, self).tearDown()

    def test_notimplemented_errors(self):
        from aerate.tests.test_fixtures import FakeDb
        data = FakeDb()
        self.assertRaises(NotImplementedError, data.create, None, None)
        self.assertRaises(NotImplementedError, data.retrieve_one, None)
        self.assertRaises(
            NotImplementedError, data.retrieve_one_raw, None, None
        )
        self.assertRaises(NotImplementedError, data.retrieve, None, None)
        self.assertRaises(
            NotImplementedError, data.update, None, None, None, None)
        self.assertRaises(NotImplementedError, data.delete, None, None)

    def test_mongo_retrieve_one_raw(self):
        config.from_pyfile('./aerate/tests/test_settings.py')
        self.db = self.pymongo[config.MONGO_DBNAME]
        self.db.pets.drop()
        obj = {config.ID_FIELD: ObjectId()}
        _id = self.db.pets.insert(obj)
        self.data = Mongo()
        self.resource = Resource(datasource='pets')
        found = self.data.retrieve_one_raw(self.resource, _id)
        self.assertTrue(found == obj)

    def test_mongo_init_with_no_config(self):
        config.reset()
        self.assertRaises(ConnectionException, Mongo)

    def test_mongo_with_alt_id_field(self):
        config.from_pyfile('./aerate/tests/test_settings.py')
        config.set('ID_FIELD', 'other_id')
        self.db = self.pymongo[config.MONGO_DBNAME]
        self.db.pets.drop()
        this_id = ObjectId()
        obj = {config.ID_FIELD: this_id}
        self.db.pets.insert(obj)
        self.data = Mongo()
        self.resource = Resource(id_field=config.ID_FIELD, datasource='pets')
        found = self.data.retrieve_one_raw(self.resource, this_id)
        self.assertTrue(found == obj)

    def test_mongo_create_one(self):
        config.from_pyfile('./aerate/tests/test_settings.py')
        self.db = self.pymongo[config.MONGO_DBNAME]
        self.db.pets.drop()
        self.data = Mongo()
        self.resource = Resource(datasource='pets')
        one_pet = {'name': 'Maebe', 'type': 'dog'}
        a = self.data.create(self.resource, one_pet)
        self.assertTrue(isinstance(a, type(ObjectId())))

    def test_mongo_create_many(self):
        config.from_pyfile('./aerate/tests/test_settings.py')
        self.db = self.pymongo[config.MONGO_DBNAME]
        self.db.pets.drop()
        self.data = Mongo()
        self.resource = Resource(datasource='pets')
        two_pets = [
            {'name': 'Maebe', 'type': 'dog'},
            {'name': 'Mimsy', 'type': 'cat'}
        ]
        a = self.data.create(self.resource, two_pets)
        self.assertTrue(len(a) == len(two_pets))

    def test_objects_have_creation_time(self):
        config.from_pyfile('./aerate/tests/test_settings.py')
        config.CREATED = 'created'
        self.db = self.pymongo[config.MONGO_DBNAME]
        self.db.pets.drop()
        self.data = Mongo()
        self.resource = Resource(datasource='pets')
        one_pet = {'name': 'Maebe', 'type': 'dog'}
        a = self.data.create(self.resource, one_pet)
        found = self.data.retrieve_one_raw(self.resource, a)
        self.assertTrue(config.CREATED in found)

    def one_test_objects_do_not_have_creation_time_if_created_not_set(self):
        config.from_pyfile('./aerate/tests/test_settings.py')
        config.CREATED = None
        self.db = self.pymongo[config.MONGO_DBNAME]
        self.db.pets.drop()
        self.data = Mongo()
        self.resource = Resource(datasource='pets')
        one_pet = {'name': 'Maebe', 'type': 'dog'}
        a = self.data.create(self.resource, one_pet)
        found = self.data.retrieve_one_raw(self.resource, a)
        self.assertTrue(config.CREATED not in found)

    def many_test_objects_do_not_have_creation_time_if_created_not_set(self):
        config.from_pyfile('./aerate/tests/test_settings.py')
        config.CREATED = None
        self.db = self.pymongo[config.MONGO_DBNAME]
        self.db.pets.drop()
        self.data = Mongo()
        self.resource = Resource(datasource='pets')
        two_pets = [
            {'name': 'Maebe', 'type': 'dog'},
            {'name': 'Mimsy', 'type': 'cat'}
        ]
        a = self.data.create(self.resource, two_pets)
        for pet in a:
            found = self.data.retrieve_one_raw(self.resource, pet)
            self.assertTrue(config.CREATED not in found)
