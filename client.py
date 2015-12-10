import os
import sys
import struct
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado import options
from tornado import ioloop
from tornado.tcpclient import TCPClient
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from common.utils import print_
from common.handler import BaseHandler
from common.messages import Message
from common.exceptions import EXCEPTION_CODES


options.define("host", default="127.0.0.1", help="HOST", group="connect")
options.define("port", type=int, default=8888, help="PORT", group="connect")
options.options.parse_command_line()

EXECUTOR = ThreadPoolExecutor(1)


def print_help():
    text = """Синтаксис:\n
        COMMAND:[arg]\n
        COMMAND - команда для отправки на сервер, по умолчанию MESS\n
        \n
        Список команд:\n
        LOGIN - авторизация пользователя в системе или смена имени пользователя, arg - имя пользователя\n
        JOIN - войти в комнату, arg - название комнаты\n
        LEFT - отписаться от комнаты, arg - название комнаты\n
        MESS(default) - отправить сообщения, arg - сообщение\n
        HELP - выводить HELP"""
    print_(text)


# Обработчик запросов пользователя
class UserHandler(BaseHandler):
    # Список допустимых команд
    allowed_commands = ['login', 'left', 'join', 'mess', 'help']

    def __init__(self, stream, app):
        self._stream = stream
        self._app = app

    @gen.coroutine
    def execute_command(self, command, text):
        handler = self._get_handler(command)
        if handler is None:
            raise ValueError("Command: {0} does not exists".format(command))
        request = handler(text)
        if request:
            yield self._stream.write(request.pack())

    def help(self, *args, **kwargs):
        print_help()

    def login(self, username):
        self._app.user = None
        return Message("LOGIN", kwargs={"username": username, "response_command": "set_user"})

    def left(self, room):
        if self._app.room == room:
            self._app.room = None
        return Message("LEFT", kwargs={"user": self._app.user, "room": room})

    def join(self, room):
        self._app.room = None
        return Message("JOIN", kwargs={"user": self._app.user, "room": room, "response_command": "set_room"})

    def mess(self, mess):
        return Message("MESS", kwargs={"user": self._app.user, "room": self._app.room, "message": mess})


class NotificationHandler(BaseHandler):

    allowed_commands = ['set_user', 'set_room', 'join', 'left', 'mess', 'resp']

    def __init__(self, request, app):
        super().__init__(request)
        self._app = app

    def process_request(self):
        handler = self._get_handler(self._request.command)
        if handler is not None:
            message = handler()
            if message: print_(message)

    def resp(self):
        if self._request.kwargs['code'] in EXCEPTION_CODES:
            date = self._request.kwargs['date']
            message = self._request.kwargs['message']
            print_("[{date}]-[ERROR]: {message}".format(date=date, message=message))

    def set_user(self):
        self._app.user = user = self._request.kwargs['user']
        date = self._request.kwargs['date']
        return '[{date}]: You are login as: "{user}"'.format(date=date, user=user)

    def set_room(self):
        self._app.room = room = self._request.kwargs['room']
        date = self._request.kwargs['date']
        return '[{date}]: You have joined the room: "{room}"'.format(date=date, room=room)

    def join(self):
        room = self._request.kwargs['room']
        date = self._request.kwargs['date']
        user = self._request.kwargs['user']
        return '[{date}]-[{room}]: User: {user} have joined the room'.format(date=date, room=room, user=user)

    def left(self):
        room = self._request.kwargs['room']
        user = self._request.kwargs['user']
        date = self._request.kwargs['date']
        return '[{date}]: User: {user} leave the room'.format(date=date, room=room, user=user)

    def mess(self):
        date = self._request.kwargs['date']
        user = self._request.kwargs['user']
        room = self._request.kwargs['room']
        message = self._request.kwargs['message']
        return '[{date}]-[{room}]-{user}: {message}'.format(date=date, room=room, user=user, message=message)


# Клиентское прилоежние
class Application():

    user_handler = UserHandler
    notification_handler = NotificationHandler

    def __init__(self, stream):
        self._stream = stream
        self._room = None
        self._user = None
        self._running = True
        self.ioloop = ioloop.IOLoop.instance()

    @property
    def stream(self):
        return self._stream

    @property
    def user(self):
        return self._user

    @property
    def room(self):
        return self._room

    @user.setter
    def user(self, user):
        self._user = user

    @room.setter
    def room(self, room):
        self._room = room

    def _parse_command(self, s):
        index = s.find(":")
        if index >= 0:
            command = s[0:index]
            text = s[index+1:]
        else:
            command = "MESS"
            text = s
        return command.lower(), text

    @gen.coroutine
    def _notification(self):
        while self._running:
            try:
                message_length = yield self._stream.read_bytes(2)
                length = struct.unpack("!H", message_length)[0]
                message = yield self._stream.read_bytes(length)
                request = Message.unpack(message)
                handler = self.notification_handler(request, self)
                handler.process_request()
            except OSError as e:
                print_(e)
                self.stop()
            except Exception as e:
                print_(e)
                self.stop()

    @gen.coroutine
    def _worker(self):
        print_help()
        while self._running:
            try:
                s = yield EXECUTOR.submit(lambda: input('> '))
                command, text = self._parse_command(s)
                handler = self.user_handler(self.stream, self)
                yield handler.execute_command(command, text)
            except Exception as e:
                print_(e)

    def run(self):
        self.ioloop.add_callback(self._notification)
        self.ioloop.add_callback(self._worker)
        return self

    def stop(self):
        self._running = False
        EXECUTOR.shutdown(False)
        self.ioloop.stop()


@gen.coroutine
def main():
    factory = TCPClient()
    stream = yield factory.connect(**options.options.group_dict("connect"))
    app = Application(stream)
    app.run()

if __name__ == '__main__':
    try:
        main()
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        EXECUTOR.shutdown(False)
        ioloop.IOLoop.instance().stop()