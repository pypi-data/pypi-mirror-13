from aerate.tests import TestBase
from aerate.tests.test_fixtures import PetCollection
from aerate import Aerate
from falcon import HTTPBadRequest, HTTPError
from falcon import testing as test
from aerate.validate import validate_partial_object
from aerate.validate import validate_object
from falcon import Request
import json


class TestValidation(TestBase):

    def setUp(self):
        super(TestValidation, self).setUp()
        from aerate.auth import BasicAuth
        from aerate.validate import Validate
        self.validate = Validate()
        self.app = Aerate(
            spec_file='./aerate/tests/petstore_simple.json',
            auth=[BasicAuth()]
        )
        self.resource = PetCollection(definition='Pet')
        self.app.add_resource(self.resource)
        self.valid = {'name': 'fido', 'id': 23, 'tag': 'this tag'}
        self.partial = {'name': 'fido', 'id': 23}
        self.partial_extra = {'name': 'fido', 'extra': 23}
        self.extra = {
            'name': 'fido', 'id': 23, 'tag': 'this tag', 'foo': 'bar'
        }

    def test_resource_spec_in_res_object(self):
        self.assertTrue(getattr(self.resource, 'schema') is not None)

    def test_validate_object_passes(self):
        self.assertTrue(validate_object(self.resource.schema, self.valid))

    def test_validate_object_list_passes(self):
        obj = [self.valid, self.valid]
        self.assertTrue(validate_object(self.resource.schema, *obj))

    def test_validate_object_fails_with_missing_field(self):
        self.assertRaises(
            HTTPBadRequest,
            validate_object,
            self.resource.schema,
            self.partial)

    def test_validate_partial_object_fails_with_extra_field(self):
        self.assertRaises(
            HTTPBadRequest,
            validate_partial_object,
            self.resource.schema,
            self.extra)

    def test_validate_partial_object_list_fails_with_extra_field(self):
        obj = [self.valid, self.partial_extra]
        self.assertRaises(
            HTTPBadRequest,
            validate_partial_object,
            self.resource.schema,
            *obj)

    def test_validate_partial_object_passes(self):
        self.assertTrue(
            validate_partial_object(self.resource.schema, self.partial)
        )

    def test_validate_partial_object_list_passes(self):
        obj = [self.partial, self.partial]
        self.assertTrue(validate_partial_object(self.resource.schema, *obj))

    def test_validate_object_fails_with_extra_field(self):
        self.assertRaises(
            HTTPBadRequest,
            validate_object,
            self.resource.schema,
            self.extra)

    def test_validate_object_list_fails_with_extra_field(self):
        self.assertRaises(
            HTTPBadRequest,
            validate_object,
            self.resource.schema,
            *[self.valid, self.extra])

    def test_validate_calls_validate_object_on_post(self):
        obj = self.valid
        env = test.create_environ(
            path='/',
            method='POST',
            body=json.dumps(obj),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertTrue(self.validate(req, resp, self.resource))

    def test_validate_returns_bad_request_if_no_body(self):
        self.env = test.create_environ(
            path='/',
            method='POST',
            body=None,
            headers={'Content-Type': 'application/json'})
        self.req = Request(self.env)
        self.resp = None
        self.assertRaises(
            HTTPBadRequest,
            self.validate,
            self.req,
            self.resp,
            self.resource
        )

    def test_validate_returns_bad_request_if_content_type_isnt_json(self):
        env = test.create_environ(
            path='/',
            method='POST',
            body=None,
            headers={'Content-Type': 'not/text'})
        req = Request(env)
        resp = None
        self.assertRaises(
            HTTPError,
            self.validate,
            req,
            resp,
            self.resource
        )

    def test_validate_returns_malformed_json_if_body_isnt_json(self):
        env = test.create_environ(
            path='/',
            method='POST',
            body='{sf:afad,}{s}',
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertRaises(
            HTTPError,
            self.validate,
            req,
            resp,
            self.resource
        )

    def test_validate_returns_true_if_method_is_GET(self):
        env = test.create_environ(
            path='/',
            method='GET',
            body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertTrue(self.validate(req, resp, self.resource))

    def test_validate_returns_true_if_method_is_HEAD(self):
        env = test.create_environ(
            path='/',
            method='HEAD',
            body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertTrue(self.validate(req, resp, self.resource))

    def test_validate_returns_true_if_method_is_DELETE(self):
        env = test.create_environ(
            path='/',
            method='DELETE',
            body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/json'})
        req = Request(env)
        resp = None
        self.assertTrue(self.validate(req, resp, self.resource))

    def test_validate_bad_content_type_raises_HTTPError(self):
        env = test.create_environ(
            path='/',
            method='GET',
            body=json.dumps({'sf': 'afad'}),
            headers={'Content-Type': 'application/xml'})
        req = Request(env)
        resp = None
        self.assertRaises(
            HTTPError,
            self.validate,
            req, resp, self.resource
        )
