from falcon import testing as test
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

    def test_create_aerate(self):
        test_app = Aerate(
            spec_file='./aerate/tests/petstore_simple.json'
        )
        from test_fixtures import PetCollection, PetItem
        self.pet_collection = PetCollection()
        self.pet_item = PetItem()
        self.assertTrue(test_app)


class TestSwagger(TestBase):

    def setUp(self):
        super(TestSwagger, self).setUp()

    def test_create_swagger_object(self):
        from aerate import Swagger
        this_swagger = Swagger()
        self.assertTrue(this_swagger.__class__.__name__ == 'Swagger')


class TestAuth(TestBase):

    def setUp(self):
        super(TestAuth, self).setUp()
