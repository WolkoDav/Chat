import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from tornado import gen
from tornado import options
from tornado import ioloop

from common.protocol import Protocol
from common.tcpserver import TCPServer
from common.handler import BaseHandler
from common.auth import authenticated
from common.storage import Storage


options.define("address", default="127.0.0.1", help="HOST", group="listen")
options.define("port", type=int, default=8888, help="PORT", group="listen")
options.options.parse_command_line()


class ChatHandler(BaseHandler):
    allowed_commands = ['login', 'join', 'left', 'mess']

    def login(self, request):
        username = self.get_argument("username")
        self._storage.set_user(username, self._socket_id)
        self.write(user_id=username)

    @authenticated
    @gen.coroutine
    def join(self, request):
        room = self.get_argument("room")
        user_id = self.get_argument("user_id")
        yield self._storage.subscribe(room, user_id)

    @authenticated
    @gen.coroutine
    def left(self, request):
        user_id = self.get_argument("user_id")
        room = self.get_argument("room")
        yield self._storage.unsubscribe(room, user_id)

    @authenticated
    @gen.coroutine
    def mess(self, request):
        user_id = self.get_argument("user_id")
        room = self.get_argument("room")
        message = self.get_argument("message")
        yield self._storage.notification(room, user_id, message)


class ChatServer(TCPServer):
    protocol = Protocol
    handler = ChatHandler
    storage = Storage


if __name__ == "__main__":
    server = ChatServer()
    server.listen(**options.options.group_dict("listen"))
    ioloop.IOLoop.current().start()