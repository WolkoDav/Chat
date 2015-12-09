from tornado import gen

from .messages import Message
from .utils import Singleton
from .exceptions import ValueException

__all__ = ['Storage', ]


# Подобие локальной БД или Redis
class Storage(metaclass=Singleton):

    def __init__(self):
        self._users = {}
        self._streams = {}
        self._rooms = {}

    def get_streams(self, room):
        return [self._streams[self._users[user_id]] for user_id in self._rooms[room]]

    def set_stream(self, id_, stream):
        self._streams[id_] = stream

    def get_stream(self, id_):
        return self._streams[id_]

    def set_room(self, room):
        if room is not None and room not in self._rooms:
            self._rooms[room] = set()
        else:
            raise ValueException("Room should not be empty")

    def set_user(self, user, stream_id):
        if user is not None and stream_id is not None and user not in self._users:
            self._users[user] = stream_id
        else:
            raise ValueException("Username: {0} is already user".format(user))

    @gen.coroutine
    def disconnect(self, stream_id):
        user = None
        for user_id in self._users:
            if self._users[user_id] == stream_id:
                user = user_id
                break
        if user is not None:
            yield [self.unsubscribe(user, room) for room in self._rooms]
            self._users.pop(user)
        self._streams.pop(stream_id)

    @gen.coroutine
    def subscribe(self, user, room):
        self.set_room(room)
        if user not in self._rooms[room]:
            request = Message("JOIN", kwargs={"user": user, "room": room})
            yield [s.write(request.pack()) for s in self.get_streams(room)]
            self._rooms[room].add(user)

    @gen.coroutine
    def unsubscribe(self, user, room):
        if room in self._rooms and user in self._rooms[room]:
            self._rooms[room].remove(user)
            request = Message("LEFT", kwargs={"user": user, "room": room})
            yield [s.write(request.pack()) for s in self.get_streams(room)]

    @gen.coroutine
    def notification(self, user, room, message):
        if room is None or user is None:
            raise ValueException("Room or Username should not be empty")
        if room in self._rooms and user in self._rooms[room]:
            request = Message("MESS", kwargs={"user": user, "room": room, "message": message})
            yield [s.write(request.pack()) for s in self.get_streams(room)]