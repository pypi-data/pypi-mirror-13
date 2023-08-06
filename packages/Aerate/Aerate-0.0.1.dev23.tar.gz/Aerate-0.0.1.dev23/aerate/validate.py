import falcon
import json


class Validate():

    def __call__(self, req, resp, res, **kwargs):
        if validate_content_type(req, resp, res, **kwargs):
            return res.validate(req.method)(req, resp, **kwargs)
        return False

    def __init__(self, req=None, resp=None, resource=None, **kwargs):
        pass


def validate_partial_object(schema, *objects):
    properties = schema['properties'].keys()
    # Make sure all keys in this object are resource schema definition.
    # We do not need to ensure all properties are in the object because
    # PATCH is a partial update.
    msg = ''
    valid = True
    for obj in objects:
        diff = set(obj.keys()) - set(properties)
        if diff:
            valid = False
            msg += str(
                ["{0} in object, but not in schema. ".format(x)
                    for x in diff]
            )
    if msg:
        raise falcon.HTTPBadRequest('Validation error', msg)
    return valid


def validate_object(schema, *objects):
    properties = schema['properties'].keys()
    # Make sure there are no differences between the properties in this object
    # and the schema definition.
    msg = ''
    valid = True
    for obj in objects:
        diff = set(obj.keys()).symmetric_difference(set(properties))
        if diff:
            valid = False
            msg += str(["{0} in schema, but not in object. ".format(x)
                        for x in set(properties) - set(obj.keys())])
            msg += str(["{0} in object, but not in schema. ".format(x)
                        for x in set(obj.keys()) - set(properties)])
    if not valid:
        raise falcon.HTTPBadRequest('Validation error', msg)
    return valid


def validate_content_type(req, resp, res, **kwargs):
    """
    Validate request Content-Type Header.

    TODO: Update this function to deal with resource-specific content-type.
    """
    contentType = req.get_header('Content-Type')
    # TODO: contentType check should use resource schema definition of
    # consumes.
    if "application/json" == contentType:
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest(
                'Empty request body',
                'A valid JSON document is required.')

        try:
            req.context['json'] = json.loads(
                body.decode('utf-8'))
            # Make sure all requests are lists for validation
            if type(req.context['json']) is not list:
                req.context['json'] = [req.context['json']]

        except (ValueError, UnicodeDecodeError):
            msg = 'Could not decode the request body. '
            msg += 'The JSON was incorrect or not encoded as UTF-8.'
            raise falcon.HTTPError(
                falcon.HTTP_753,
                'Malformed JSON', msg)
    else:
        raise falcon.HTTPError(
            falcon.HTTP_400,
            'Bad Content-Type Header',
            'Content-Type must be "application/json"')
    return True
