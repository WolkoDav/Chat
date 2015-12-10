# coding: utf-8
import os
import sys
from tornado import gen
from tornado import options
from tornado import ioloop
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from common.protocol import Protocol
from common.tcpserver import TCPServer
from common.handler import ServerHandler
from common.auth import authenticated
from common.storage import Storage


options.define("address", default="127.0.0.1", help="HOST", group="listen")
options.define("port", type=int, default=8888, help="PORT", group="listen")
options.options.parse_command_line()


# Обработчик запрос
class ChatHandler(ServerHandler):
    allowed_commands = ['login', 'join', 'left', 'mess']

    @gen.coroutine
    def login(self, request):
        username = self.get_argument("username")
        self._storage.set_user(username, self._socket_id)
        self.write(user=username)

    @gen.coroutine
    @authenticated
    def join(self, request):
        room = self.get_argument("room")
        user = self.get_argument("user")
        self.write(room=room)
        yield self._storage.subscribe(user=user, room=room)

    @gen.coroutine
    @authenticated
    def left(self, request):
        room = self.get_argument("room")
        user = self.get_argument("user")
        yield self._storage.unsubscribe(user=user, room=room)

    @gen.coroutine
    @authenticated
    def mess(self, request):
        user = self.get_argument("user")
        room = self.get_argument("room")
        message = self.get_argument("message")
        yield self._storage.notification(user=user, room=room, message=message)


# Чат сервер
class ChatServer(TCPServer):
    protocol = Protocol
    handler = ChatHandler
    storage = Storage


# Запуск
if __name__ == "__main__":
    server = ChatServer()
    server.listen(**options.options.group_dict("listen"))
    ioloop.IOLoop.current().start()