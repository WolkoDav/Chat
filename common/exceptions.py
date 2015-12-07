class ChatException(Exception):
    code = None


class AuthException(ChatException):
    code = 3


class MethodNotExists(ChatException):
    code = 4
