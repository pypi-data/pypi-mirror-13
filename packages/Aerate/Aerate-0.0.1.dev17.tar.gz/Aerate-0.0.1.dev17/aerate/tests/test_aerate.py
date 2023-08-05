from falcon import testing as test
from falcon import Request
from aerate import Aerate

class TestBase(test.TestBase):

    def setUp(self):
        # Create a mock application:
        self.srmock = test.StartResponseMock()
        self.app = Aerate(
            spec_file='./aerate/tests/petstore_simple.json',
        )

    def simulate_request(self, path, *args, **kwargs):

        env = test.create_environ(
            path=path, **kwargs)
        return self.app(env, self.srmock)

    def simulate_get(self, *args, **kwargs):
        kwargs['method'] = 'GET'
        return self.simulate_request(*args, **kwargs)

    def simulate_post(self, *args, **kwargs):
        kwargs['method'] = 'POST'
        return self.simulate_request(*args, **kwargs)

    def simulate_delete(self, *args, **kwargs):
        kwargs['method'] = 'DELETE'
        return self.simulate_request(*args, **kwargs)


class TestInitializeAerate(TestBase):

    def setUp(self):
        super(TestInitializeAerate, self).setUp()
        from test_fixtures import PetCollection, PetItem
        self.pet_collection = PetCollection()
        self.pet_item = PetItem()
        self.spec_file = './aerate/tests/petstore_simple.json'
        self.test_app = Aerate(spec_file=self.spec_file)

    def test_create_aerate(self):
        self.assertTrue(self.test_app)

    def test_add_resource(self):

        self.test_app.add_resource(self.pet_item)

        self.assertTrue(0 < len(self.test_app.resource_list))
        self.assertTrue('PetItem' in self.test_app.resource_list)
        self.assertTrue(0 < len(self.test_app.op_dict))
        self.assertTrue('PetItem_on_get' in self.test_app.op_dict)
        self.assertTrue('PetItem_on_delete' in self.test_app.op_dict)
        self.assertFalse('PetItem_on_update' in self.test_app.op_dict)
        self.assertFalse('PetItem_on_post' in self.test_app.op_dict)

    def test_add_resource_op_middleware(self):
        self.test_app.add_resource(self.pet_item)

        self.assertIsNotNone( self.test_app._opMiddleware )
        self.assertIsNotNone( self.test_app._opMiddleware.ops )
        self.assertTrue('PetItem_on_get' in self.test_app._opMiddleware.ops )
        self.assertTrue('PetItem_on_delete' in self.test_app._opMiddleware.ops )

    def test_add_resource_with_middleware(self):
        self._before = ['test_middleware']
        self.test_app.add_resource( self.pet_item)
        self.assertEquals(1, len(self._before))

    def test_add_resource_bad_object(self):
        from test_fixtures import Foo
        with self.assertRaises(ValueError):
            self.test_app.add_resource( Foo() )

    def test_add_resource_with_no_auth_initialized(self):
        with self.assertRaises(KeyError):
            self.test_app.add_resource( self.pet_collection)

    def test_add_resource_with_auth_initialized(self):
        from aerate.auth import BasicAuth
        b = BasicAuth()
        app = Aerate(spec_file=self.spec_file,
                    auth=[b]
        )
        self.assertTrue( 0 == len(app._before) )
        app.add_resource( self.pet_collection)
        # resoure, method_map, params = app._router.find('/api/pets')
        self.assertTrue( 1 == len(app._middleware) )
        self.assertTrue( 0 == len(app._before) )

    def test_add_auth(self):
        from aerate.auth import BasicAuth
        b = BasicAuth()
        app = Aerate(spec_file=self.spec_file,
                    auth=[b]
        )
        app.add_resource( self.pet_collection)
        auths = app.swagger._get_security('PetCollection_on_post')
        self.assertEquals(1, len(auths))

        self.assertTrue( 0 == len(app._before) )
        app._add_auths_to_route([b])
        self.assertTrue( 3 == len(app._before) )
        app._remove_auths_from_global([b])
        self.assertTrue( 0 == len(app._before) )


class TestSwagger(TestBase):

    def setUp(self):
        super(TestSwagger, self).setUp()

    def test_create_swagger_object(self):
        from aerate import Swagger
        this_swagger = Swagger()
        self.assertTrue(this_swagger.__class__.__name__ == 'Swagger')

    def test_create_with_none(self):
        from aerate import Swagger
        from bravado_core.exception import SwaggerSchemaError
        swaggerspec = {"swagger": "2.0"}
        #the following does not like SwaggerValidationError for some reason
        with self.assertRaises(Exception):
            this_swagger = Swagger(swaggerspec)

class TestAuth(TestBase):

    def setUp(self):
        super(TestAuth, self).setUp()


class TestOpMiddleware(TestBase):

    def setUp(self):
        super(TestOpMiddleware, self).setUp()

        from test_fixtures import PetItem
        self.pet_item = PetItem()
        #falcon.testing.create_environ(path='/', query_string='', protocol='HTTP/1.1', scheme='http', host='falconframework.org', port=None, headers=None, app='', body='', method='GET', wsgierrors=None, file_wrapper=None)
        env = test.create_environ(path='/', method='GET')
        self.req = Request(env)

        from aerate.middleware import OpMiddleware
        self.opMiddleware = OpMiddleware()

    def test_ops(self):
        self.assertEquals(0, len(self.opMiddleware.ops))

    def test_process(self):
        self.opMiddleware.ops['PetItem_on_get'] = "test"
        self.opMiddleware.process_resource( self.req, None, self.pet_item)

    def test_process_bad_key(self):
        self.opMiddleware.ops['nothesame'] = "test"
        with self.assertRaises(KeyError):
            self.opMiddleware.process_resource( self.req, None, self.pet_item)
