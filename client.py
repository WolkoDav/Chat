import os
import sys
import struct
import socket
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import readline

from tornado import gen
from tornado import options
from tornado import ioloop
from tornado.tcpclient import TCPClient

from common.messages import Message


options.define("host", default="127.0.0.1", help="HOST", group="connect")
options.define("port", type=int, default=8888, help="PORT", group="connect")
options.options.parse_command_line()


@gen.coroutine
def notification(stream):
    message_length = yield stream.read_bytes(2)
    length = struct.unpack("!H", message_length)[0]
    message = yield stream.read_bytes(length)
    # request = Message.unpack(message=message)
    sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())+2)+'\r')
    print(message)
    sys.stdout.write('> ' + readline.get_line_buffer())
    sys.stdout.flush()
    ioloop.IOLoop.instance().add_callback(notification, stream)


class UserHandler():
    allowed_command = ['login', 'left', 'join', 'mess']

    def __init__(self, stream, app):
        self._stream = stream
        self._app = app

    @gen.coroutine
    def execute_command(self, command, text):
        handler = None
        if command in self.allowed_command:
            handler = getattr(self, command, None)
        if handler is None:
            raise ValueError("Command does not exists")
        yield handler(text)

    @gen.coroutine
    def login(self, username):
        request = Message("LOGIN", kwargs={"username": username})
        yield self._stream.write(request.pack())

    @gen.coroutine
    def left(self, room):
        if self._app.room == room:
            self._app.room = None
        request = Message("LEFT", kwargs={"user_id": self._app.user, "room": room})
        yield self._stream.write(request.pack())

    @gen.coroutine
    def join(self, room):
        self._app.room = room
        request = Message("JOIN", kwargs={"user_id": self._app.user, "room": room})
        yield self._stream.write(request.pack())

    @gen.coroutine
    def mess(self, mess):
        request = Message("JOIN", kwargs={"user_id": self._app.user, "room": self._app.room, "mess": mess})
        yield self._stream.write(request.pack())


class Application():

    handler = UserHandler

    def __init__(self, stream):
        self._stream = stream
        self.room = None
        self._user_id = None

    @property
    def user(self):
        return self._user_id

    @property
    def room(self):
        return self.__room

    @room.setter
    def room(self, room):
        self.__room = room

    def _parse_command(self, s):
        index = s.find(":")
        command = s[0:index]
        text = s[index+1:]
        return command.lower(), text

    @gen.coroutine
    def run(self):
        while True:
            try:
                s = input('> ')
                command, text = self._parse_command(s)
                handler = self.handler(self._stream, self)
                yield handler.execute_command(command, text)
            except Exception as e:
                print(e)


@gen.coroutine
def main():
    factory = TCPClient()
    stream = yield factory.connect(af=socket.AF_INET, **options.options.group_dict("connect"))
    ioloop.IOLoop.instance().add_callback(notification, stream)
    app = Application(stream)
    app.run()

if __name__ == '__main__':
    try:
        main()
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass