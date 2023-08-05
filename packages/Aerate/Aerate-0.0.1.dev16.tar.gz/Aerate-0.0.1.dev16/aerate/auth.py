from falcon import HTTPUnauthorized


class Auth():

    def __call__(self, req, resp):

        self.authenticate(req, resp)

    def authenticate(self, req, resp):
        """
        Authenticates a request.

        This function calls a check_auth function that must return a boolean
        indicating if the auth method has succeeded. Multiple auth methods can
        be run, and as long as one is True, we will continue to return
        req.env['wsgi.authenticated'] as True.

        """
        if not req.env['wsgi.authenticated']:
            req.env['wsgi.authenticated'] = True and self.check_auth()

    def check_auth(self, req, resp):
        return NotImplementedError

    @staticmethod
    def first(req, resp):
        req.env['wsgi.authenticated'] = None

    @staticmethod
    def last(req, resp):
        if not req.env['wsgi.authenticated']:
            raise HTTPUnauthorized(
                'Unauthorized.', 'Request is not authorized.'
            )


class BasicAuth(Auth):
    """ Implements BasicAuth for Aerate


    """
    def check_auth(self, req, resp):
        return True


class JWTAuth(Auth):
    """ Implements JWT Token-based Auth for Aerate

    """
    def check_auth(self, req, resp):
        return True


class TestingAuth(Auth):
    """ Implements a testing authentication object with some usefull hooks
    for testing Aerate apps.

    """
    def check_auth(self, req, resp):
        return True
