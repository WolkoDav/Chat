import copy

from tornado import gen

from common.messages import Message
from common.exceptions import TcpException, MethodNotExists

__all__ = ['BaseHandler', ]


# Базовый обработчик запросов на сервер
class BaseHandler():

    # Список допустимых программ
    allowed_commands = []

    def __init__(self, request, socket_id, storage):
        self._request = request
        self._socket_id = socket_id
        self._storage = storage
        self._data = {}
        self._status_code = 0

    # Добавить значение в Response
    def write(self, **kwargs):
        self._data.update(kwargs)

    # Получить аргумент из Request
    def get_argument(self, argument, default=None):
        return self._request.kwargs.get(argument, default)

    # Статус ответа
    def status_code(self, code):
        self._status_code = code

    # Получить данные для Response
    @property
    def data(self):
        d = copy.deepcopy(self._data)
        d["code"] = self._status_code
        return d

    # Обработка запроса
    def process_request(self):
        handler = None
        future = gen.TracebackFuture()
        try:
            command = self._request.command.lower()
            if command in self.allowed_commands:
                handler = getattr(self, command, None)
            if handler is None:
                raise MethodNotExists(command)
            handler(self._request)
        except TcpException as e:
            self.write(message=e.message)
            self.status_code(e.code)

        response = Message("RESP", kwargs=self.data)
        future.set_result(response)
        return future