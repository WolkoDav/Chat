import struct
import socket

from tornado import gen
from tornado import iostream

from common.utils import random_string
from common.messages import Message


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

    @gen.coroutine
    def on_disconnect(self):
        yield self._storage.disconnect(self._id)

    @gen.coroutine
    def dispatch_client(self):
        try:
            while True:
                message_length = yield self._stream.read_bytes(2)
                length = struct.unpack("!H", message_length)[0]
                message = yield self._stream.read_bytes(length)
                request = Message.unpack(message=message)
                handler = self._handler(request, self._id, self._storage)
                response = yield handler.process_request()
                yield self._stream.write(response.pack())
        except iostream.StreamClosedError:
            pass

    @gen.coroutine
    def on_connect(self):
        self._storage.set_stream(self._id, self._stream)
        yield self.dispatch_client()
