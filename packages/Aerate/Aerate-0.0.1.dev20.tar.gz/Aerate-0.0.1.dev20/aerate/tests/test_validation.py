from aerate.tests import TestBase
from aerate.tests.test_fixtures import PetCollection
from aerate import Aerate
from falcon import HTTPBadRequest, HTTPError
from falcon import testing as test
from falcon import Request


class TestValidation(TestBase):

    def setUp(self):
        super(TestValidation, self).setUp()
        from aerate.auth import BasicAuth
        self.app = Aerate(
            spec_file='./aerate/tests/petstore_simple.json',
            auth=[BasicAuth()]
        )
        self.resource = PetCollection()

    def test_resource_spec_in_res_object(self):
        self.app.add_resource(self.resource)
        self.assertTrue(getattr(self.resource, 'schema') is not None)

    def test_validate_object_passes(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate_object
        obj = {'name': 'fido', 'id': 23, 'tag': 'this tag'}
        self.assertTrue(validate_object(self.resource.schema, obj))

    def test_validate_object_fails_with_missing_field(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate_object
        obj = {'name': 'fido', 'id': 23}
        self.assertRaises(
            HTTPBadRequest,
            validate_object,
            self.resource.schema,
            obj)

    def test_validate_object_fails_with_extra_field(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate_object
        obj = {'name': 'fido', 'id': 23, 'extra': 42}
        self.assertRaises(
            HTTPBadRequest,
            validate_object,
            self.resource.schema,
            obj)

    def test_validate_calls_validate_object_on_post(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate
        import json
        obj = {'name': 'fido', 'id': 23, 'tag': 42}
        env = test.create_environ(
            path='/',
            method='POST',
            body=json.dumps(obj),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertTrue(validate(req, resp, self.resource))

    def test_validate_returns_bad_request_if_no_body(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate
        env = test.create_environ(
            path='/',
            method='POST',
            body=None,
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertRaises(
            HTTPBadRequest,
            validate,
            req,
            resp,
            self.resource
        )

    def test_validate_returns_bad_request_if_content_type_isnt_json(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate
        env = test.create_environ(
            path='/',
            method='POST',
            body=None,
            headers={'Content-Type': 'not/text'})
        req = Request(env)
        resp = None
        self.assertRaises(
            HTTPError,
            validate,
            req,
            resp,
            self.resource
        )

    def test_validate_returns_malformed_json_if_body_isnt_json(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate
        env = test.create_environ(
            path='/',
            method='POST',
            body='{sf:afad,}{s}',
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertRaises(
            HTTPError,
            validate,
            req,
            resp,
            self.resource
        )

    def test_validate_returns_true_if_method_is_not_PUT_PATCH_POST(self):
        self.app.add_resource(self.resource)
        from aerate.validate import validate
        env = test.create_environ(
            path='/',
            method='GET',
            body='{sf:afad,}{s}',
            headers={'Content-Type': 'junk/json'})
        req = Request(env)
        resp = None
        self.assertTrue(validate(req, resp, self.resource))
