import falcon
import json


def validate(req, resp, res, **kwargs):

    if req.method in ['PUT', 'POST', 'PATCH']:
        contentType = req.get_header('Content-Type')
        if "application/json" == contentType:
            body = req.stream.read()
            if not body:
                raise falcon.HTTPBadRequest(
                    'Empty request body',
                    'A valid JSON document is required.')

            try:
                req.context['json'] = json.loads(
                    body.decode('utf-8'))

            except (ValueError, UnicodeDecodeError):
                raise falcon.HTTPError(
                    falcon.HTTP_753,
                    'Malformed JSON',
                    'Could not decode the request body. The '
                    'JSON was incorrect or not encoded as '
                    'UTF-8.')
        else:
            raise falcon.HTTPError(
                falcon.HTTP_400,
                'Bad Content-Type Header',
                'Content-Type must be "application/json"')
        return validate_object(res.schema, req.context['json'])
    else:
        return True


def validate_object(schema, obj):
    properties = schema['properties'].keys()
    diff = set(properties).difference(set(obj.keys()))
    if not diff:
        return True
    else:
        msg = ''
        msg += str(["{0} in schema, but not in object. ".format(x)
                    for x in set(properties) - set(obj.keys())])
        msg += str(["{0} in object, but not in schema. ".format(x)
                    for x in set(obj.keys()) - set(properties)])
        raise falcon.HTTPBadRequest('Validation error', msg)
