import struct
import socket

from tornado import gen
from tornado import iostream

from common.utils import random_string
from common.messages import Message

__all__ = ['Protocol', ]


# Протокол
class Protocol():

    def __init__(self, handler, stream, storage):
        super().__init__()
        self._id = random_string(40)
        self._stream = stream
        self._handler = handler
        self._storage = storage()

        self._stream.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._stream.socket.setsockopt(socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self._stream.set_close_callback(self.on_disconnect)

    # Закрытие сокета
    @gen.coroutine
    def on_disconnect(self):
        yield self._storage.disconnect(self._id)

    # Обработка запроса после соединения
    @gen.coroutine
    def dispatch_client(self):
        try:
            while True:
                # Считать длинну сообщения
                message_length = yield self._stream.read_bytes(2)
                # Распоковать
                length = struct.unpack("!H", message_length)[0]
                # Считать сообщение
                message = yield self._stream.read_bytes(length)
                # Распоковать запрос
                request = Message.unpack(message=message)
                # Создать обработчик запросов
                handler = self._handler(request, self._id, self._storage)
                # Обработать запрос
                response = yield handler.process_request()
                # Вернуть ответ
                yield self._stream.write(response.pack())
        except iostream.StreamClosedError:
            pass

    # Функция вызова после соединения
    @gen.coroutine
    def on_connect(self):
        self._storage.set_stream(self._id, self._stream)
        yield self.dispatch_client()
