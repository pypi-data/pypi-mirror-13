from aerate.auth import AuthProvider
from aerate.utils import log


class AerateMiddleware(object):

    def __init__(self):
        self.auth_map = {}

    """
    Handles Authorization, and Validation for Aerate
    """
    def process_resource(self, req, resp, resource, **kwargs):
        log.info("called process_resource in AerateMiddleware()")
        if resource:
            key = resource.name() + "_on_" + req.method.lower()
            if key in self.auth_map:
                a = AuthProvider(self.auth_map[key])
                a.authenticate(req, resp, **kwargs)

            resource.authorize(req.method)(req, resp, **kwargs)
            #resource.validate(req.method)(req, resp, **kwargs)


    def add_auths(self, key, auth_fns):
        self.auth_map[key] = auth_fns