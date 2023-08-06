from aerate.tests import TestBase
from aerate.tests.test_fixtures import PetCollection, PetItem
from aerate import Aerate
from falcon import testing as test
from falcon import Request
import json
from falcon import HTTPInternalServerError


class TestMiddleware(TestBase):

    def setUp(self):
        super(TestMiddleware, self).setUp()
        from aerate.auth import BasicAuth
        from aerate.validate import Validate
        self.validate = Validate()
        self.app = Aerate(
            spec_file='./aerate/tests/petstore_simple.json',
            auth=[BasicAuth()]
        )
        self.resource = PetCollection(definition='Pet')
        self.item_resource = PetItem(definition='Pet')
        self.app.add_resource(self.resource)
        self.valid = {'name': 'fido', 'id': 23, 'tag': 'this tag'}
        self.partial = {'name': 'fido', 'id': 23}
        self.partial_extra = {'name': 'fido', 'extra': 23}
        self.extra = {
            'name': 'fido', 'id': 23, 'tag': 'this tag', 'foo': 'bar'
        }
        self.middleware = self.app.aerate_middleware

    def test_process_resource_returns_true(self):
        env = test.create_environ(
            path='/',
            method='GET',
            # body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertTrue(self.middleware.process_resource(req, resp, self.resource))

    def test_process_resource_raises_server_error_if_no_resource(self):
        env = test.create_environ(
            path='/',
            method='GET',
            body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertFalse(self.middleware.process_resource(req, resp, None))

    def test_do_auths_raises_server_error_no_auth_key(self):
        env = test.create_environ(
            path='/',
            method='BAD_METHOD',
            body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertRaises(
            ValueError,
            self.middleware.do_auths,
            req, resp, self.resource, None
        )

    def test_do_auths_passes_if_request_is_not_in_auth_map(self):
        env = test.create_environ(
            path='/',
            method='GET',
            body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertTrue(
            self.middleware.do_auths(
                req, resp, self.item_resource, key='GET'
            )
        )
