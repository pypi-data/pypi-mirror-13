from falcon import HTTPUnauthorized


class Auth():

    def __call__(self, req, resp, resource, **params):
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
            req.env['wsgi.authenticated'] = True and self.check_auth(req, resp)

    def check_auth(self, req, resp):
        raise NotImplementedError

    @staticmethod
    def first(req, resp, resource, **kwargs):
        req.env['wsgi.authenticated'] = None

    @staticmethod
    def last(req, resp, resource, **kwargs):
        if not req.env['wsgi.authenticated']:
            raise HTTPUnauthorized(
                'Unauthorized.', 'Request is not authorized.'
            )

    @staticmethod
    def _wrap_auths(auths=None):
        if Auth.first == auths[-1] and Auth.last == auths[0]:
            return auths
        if auths:
            # insert in reverse order, because deque reverses order.
            auths.append(Auth.first)
            auths.insert(0, Auth.last)
        return auths


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
