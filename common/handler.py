import copy

from tornado import gen

from common.messages import Message
from common.exceptions import ChatException, MethodNotExists


class BaseHandler():

    allowed_commands = []

    def __init__(self, request, socket_id):
        self._request = request
        self._socket_id = socket_id
        self._data = {}
        self._status_code = 0

    def write(self, **kwargs):
        self._data.update(kwargs)

    def get_argument(self, argument, default=None):
        return self._request.kwargs.get(argument, default)

    def status_code(self, code):
        self._status_code = code

    @property
    def data(self):
        d = copy.deepcopy(self._data)
        d["code"] = self._status_code
        return d

    def process_request(self):
        handler = None
        future = gen.TracebackFuture()
        command = self._request.command.lower()
        try:
            if command in self.allowed_commands:
                handler = getattr(self, command, None)
            if handler is None:
                raise MethodNotExists()
            handler(self._request)
        except ChatException as e:
            self.status_code(e.code)
        except Exception as e:
            self.status_code(5)

        response = Message("RESP", kwargs=self.data)
        future.set_result(response)
        return future