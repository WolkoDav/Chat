from .exceptions import AuthException

__all__ = ['authenticated', ]


# Декоратор для проверки авторизации
def authenticated(fn):
    def wrapper(self, request):
        if self.get_argument("user") is None:
            raise AuthException()
        return fn(self, request)
    return wrapper