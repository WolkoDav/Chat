from .exceptions import AuthException


def authenticated(fn):
    def wrapper(*args, **kwargs):
        if "user_id" not in kwargs:
            raise AuthException()
        return fn(*args, **kwargs)
    return wrapper