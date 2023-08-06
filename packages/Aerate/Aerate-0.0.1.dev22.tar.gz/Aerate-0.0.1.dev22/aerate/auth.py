from falcon import HTTPUnauthorized, HTTPForbidden


class Auth():

    def __call__(self, req, resp, resource, **params):
        self.authenticate(req, resp, resource)

    def authenticate(self, req, resp, resource):
        """
        Authenticates a request.

        This function calls a check_auth function that must return a boolean
        indicating if the auth method has succeeded. Multiple auth methods can
        be run, and as long as one is True, we will continue to return
        req.env['wsgi.authenticated'] as True.

        """
        if not req.env['wsgi.authenticated']:
            req.env['wsgi.authenticated'] = True and self.check_auth(
                req, resp, resource)

    def check_auth(self, req, resp, resource):
        raise NotImplementedError

    @staticmethod
    def first(req, resp, resource, **kwargs):
        req.env['wsgi.authenticated'] = None

    @staticmethod
    def _wrap_auths(auths=None):
        if Auth.first == auths[-1]: #and Auth.last == auths[0]:
            return auths
        if auths:
            # insert in reverse order, because deque reverses order.
            auths.append(Auth.first)
            auths.insert(0, LastAuth)
        return auths

class LastAuth():

    def __call__(self, req, resp, resource, **params):
        self.auth(req, resp, resource, **params)

    def __init__(self, req=None, resp=None, resource=None, **kwargs):
        pass

    def auth(self, req, resp, resource, **kwargs):
        '''
        fires at the end of the chain of auth functions
        '''
        # if none of the authenticator providers set this env variable
        # the users isn't allowed to go any further
        if not req.env['wsgi.authenticated']:
            raise HTTPUnauthorized(
                'Unauthorized.', 'User is not authenticated.'
            )
        # otherwise get the authorize function off the resource and call it
        # so the resource itself can tell us that  we are allowed
        authorize = resource.authorize[req.method]
        if authorize:
            if authorize(req, resp, **kwargs):
                return
        raise HTTPForbidden('Forbidden', 'Unauthorized')


class BasicAuth(Auth):
    """ Implements BasicAuth for Aerate


    """
    def check_auth(self, req, resp, resource):
        return True


class JWTAuth(Auth):
    """ Implements JWT Token-based Auth for Aerate

    """
    def check_auth(self, req, resp, resource):
        return True


class TestingAuth(Auth):
    """ Implements a testing authentication object with some usefull hooks
    for testing Aerate apps.

    """
    def check_auth(self, req, resp, resource):
        return True
