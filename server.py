import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from tornado import gen
from tornado import options
from tornado import ioloop

from common.protocol import Protocol
from common.tcpserver import TCPServer
from common.handler import BaseHandler
from common.messages import Message
from common.auth import authenticated


options.define("address", default="127.0.0.1", help="HOST", group="listen")
options.define("port", type=int, default=8888, help="PORT", group="listen")
options.options.parse_command_line()

# TODO: исправить этот костыль
stream_storage = {}
chat_storage = {}
user_stream = {}
USER_ID = 1


def get_streams(room):
    streams = []
    for user_id in room.values():
        streams.append(stream_storage[user_stream[user_id]])
    return streams


class ChatHandler(BaseHandler):
    allowed_commands = ['login', 'join', 'left', 'mess']

    def login(self, request):
        global USER_ID, user_stream
        username = self.get_argument("username")
        self.write(user_id=USER_ID)
        user_stream[USER_ID] = self._socket_id
        USER_ID += 1

    @authenticated
    @gen.coroutine
    def join(self, request):
        room = self.get_argument("room")
        user_id = self.get_argument("user_id")
        if room not in chat_storage:
            chat_storage[room] = set()
        if user_id not in chat_storage[room]:
            chat_storage[room].add(user_id)
            streams = get_streams(room)
            request = Message("JOIN", kwargs={"user_id": user_id, "room": room})
            yield [s.write(request.pack()) for s in streams]

    @authenticated
    @gen.coroutine
    def left(self, request):
        user_id = self.get_argument("user_id")
        room = self.get_argument("room")
        if room in chat_storage and user_id in chat_storage[room]:
            chat_storage[room].remove(user_id)
            streams = get_streams(room)
            request = Message("LEFT", kwargs={"user_id": user_id, "room": room})
            yield [s.write(request.pack()) for s in streams]

    @authenticated
    @gen.coroutine
    def mess(self, request):
        user_id = self.get_argument("user_id")
        room = self.get_argument("room")
        message = self.get_argument("message")
        if room in chat_storage and user_id in chat_storage[room]:
            streams = get_streams(room)
            request = Message("MESS", kwargs={"user_id": user_id, "room": room, "message": message})
            yield [s.write(request.pack()) for s in streams]


class ChatServer(TCPServer):
    protocol = Protocol
    handler = ChatHandler


if __name__ == "__main__":
    server = ChatServer()
    server.listen(**options.options.group_dict("listen"))
    ioloop.IOLoop.current().start()