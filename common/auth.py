from .exceptions import AuthException


def authenticated(fn):
    def wrapper(self, request):
        if self.get_argument("user_id") is None:
            raise AuthException()
        return fn(self, request)
    return wrapper