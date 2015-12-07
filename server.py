import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from tornado import gen
from tornado import options
from tornado import ioloop

from common.protocol import Protocol
from common.tcpserver import TCPServer
from common.handler import BaseHandler
from common.messages import Request, Response
from common.auth import authenticated
from common.exceptions import ChatException, MethodNotExists

options.define("address", default="127.0.0.1", help="HOST", group="listen")
options.define("port", type=int, default=8888, help="PORT", group="listen")
options.options.parse_command_line()

stream_storage = {}


class ChatHandler(BaseHandler):
    allowed_commands = ['login', 'join', 'left', 'mess']

    @gen.coroutine
    def disconnect(self, stream_id, stream):
        del stream_storage[stream_id]
        request = Request("DISC", kwargs={"id": stream_id})
        yield [s.write(request.pack()) for _, s in stream_storage.items()]

    @gen.coroutine
    def connect(self, stream_id, stream):
        stream_storage[stream_id] = stream

    def process_request(self):
        handler = None
        future = gen.TracebackFuture()
        command = self._request.command.lower()
        try:
            if command in self.allowed_commands:
                handler = getattr(self, command, None)
            if handler is None:
                raise MethodNotExists()
            handler(**self._request.kwargs)
            response = Response(0)
        except ChatException as e:
            future.set_exception(e)
            response = Response(e.code)
        except Exception as e:
            future.set_exception(e)
            response = Response(5)
        future.set_result(response)
        return future

    def login(self, username):
        pass

    @authenticated
    @gen.coroutine
    def join(self, user_id, room):
        request = Request("JOIN", kwargs={"user_id": user_id, "room": room})
        yield [s.write(request.pack()) for _, s in stream_storage.items()]

    @authenticated
    @gen.coroutine
    def left(self, user_id, room):
        request = Request("LEFT", kwargs={"user_id": user_id, "room": room})
        yield [s.write(request.pack()) for _, s in stream_storage.items()]

    @authenticated
    @gen.coroutine
    def mess(self, user_id, room, message):
        request = Request("MESS", kwargs={"user_id": user_id, "room": room, "message": message})
        yield [s.write(request.pack()) for _, s in stream_storage.items()]


class ChatServer(TCPServer):
    protocol = Protocol
    handler = ChatHandler


if __name__ == "__main__":
    server = ChatServer()
    server.listen(**options.options.group_dict("listen"))
    ioloop.IOLoop.current().start()