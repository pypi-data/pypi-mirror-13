from falcon import testing as test
from falcon import Request, HTTPUnauthorized
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

    def test_add_resource_with_middleware(self):
        self._before = ['test_middleware']
        self.test_app.add_resource( self.pet_item)
        self.assertEquals(1, len(self._before))

    def test_add_resource_bad_object(self):
        from test_fixtures import Foo
        with self.assertRaises(ValueError):
            self.test_app.add_resource( Foo() )

    def test_add_resource_http_method_mismatch_with_spec(self):
        #this should fail because XXX contains one http method and the spec specified another
        from test_fixtures import XXX
        with self.assertRaises(ValueError):
            self.test_app.add_resource(XXX())

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
        self.assertTrue( 0 == len(app._middleware) )
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

class TestAuth(TestBase):

    def setUp(self):
          super(TestAuth, self).setUp()
          from aerate.auth import Auth
          self.abstract_auth = Auth()

    def test_not_implemented_checkauth(self):
        env = test.create_environ(path='/', method='GET')
        req = Request(env)
        req.env['wsgi.authenticated'] = False
        with self.assertRaises(NotImplementedError):
            self.abstract_auth.authenticate(req, None)

    def test_no_checkauth(self):
        '''No need to call check auth because we have passed upstream'''
        env = test.create_environ(path='/', method='GET')
        req = Request(env)
        req.env['wsgi.authenticated'] = True
        self.abstract_auth.authenticate(req, None)

    def test_check__call__(self):
        env = test.create_environ(path='/', method='GET')
        req = Request(env)
        req.env['wsgi.authenticated'] = True
        self.abstract_auth(req, None, None)


    def test_testing_auth(self):
        env = test.create_environ(path='/', method='GET')
        req = Request(env)
        req.env['wsgi.authenticated'] = False
        from aerate.auth import TestingAuth
        auth = TestingAuth()
        auth.authenticate(req, None)
        self.assertTrue(req.env['wsgi.authenticated'])

    def test_first_auth(self):
        env = test.create_environ(path='/', method='GET')
        req = Request(env)
        self.assertFalse('wsgi.authenticated' in req.env)
        from aerate.auth import Auth
        Auth.first(req, None, None)
        self.assertTrue('wsgi.authenticated' in req.env)
        self.assertIsNone(req.env['wsgi.authenticated'])

    def test_last_auth(self):
        env = test.create_environ(path='/', method='GET')
        req = Request(env)
        req.env['wsgi.authenticated'] = True
        from aerate.auth import Auth
        Auth.last(req, None, None)
        self.assertTrue('wsgi.authenticated' in req.env)
        self.assertTrue(req.env['wsgi.authenticated'])

    def test_last_auth_fail(self):
        env = test.create_environ(path='/', method='GET')
        req = Request(env)
        req.env['wsgi.authenticated'] = False
        from aerate.auth import Auth
        with self.assertRaises(HTTPUnauthorized):
            Auth.last(req, None, None)