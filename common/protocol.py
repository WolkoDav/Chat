import socket

from tornado import gen
from tornado import iostream

from common.utils import random_string
from common.message import Message


class BaseProtocol():
    service = None

    def __init__(self, stream):
        super().__init__()
        self._id = random_string(40)
        self._stream = stream

        self._stream.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._stream.socket.setsockopt(socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self._stream.set_close_callback(self.on_disconnect)

    @gen.coroutine
    def on_disconnect(self):
        yield self.service.disconnect(self._id)

    @gen.coroutine
    def dispatch_client(self):
        try:
            while True:
                message_length = yield self._stream.read_bytes(2)
                message = yield self._stream.read_bytes(message_length)
                request = Message.unpack(message=message)
                response = self.service.proccess_request(request=request)
                yield self._stream.write(response.pack())
        except iostream.StreamClosedError:
            pass

    @gen.coroutine
    def on_connect(self):
        yield self.service.login(self._id)
        yield self.dispatch_client()
