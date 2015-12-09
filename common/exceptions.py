# Базовый класс для ошибок
class TcpException(Exception):
    code = 5
    message = "Server error"


# Данный метод не существует
class MethodNotExists(TcpException):
    code = 4

    def __init__(self, method):
        self.message = "Method: {0} does not exists".format(method)


#  Ошибка авторизации
class AuthException(TcpException):
    code = 3
    message = "Need authorization"


#  Ощибка значения
class ValueException(TcpException):
    code = 2

    def __init__(self, message):
        self.message = message


EXCEPTION_CODES = [2, 3, 4, 5]