import copy
import base64
import pickle
import datetime
from struct import pack


class Message():

    def __init__(self, command, kwargs):
        self._command = command
        self._kwargs = kwargs

    @property
    def command(self):
        return self._command

    @property
    def kwargs(self):
        return self._kwargs

    def pack(self):
        m = []
        kw = copy.deepcopy(self.kwargs)
        kw["date"] = datetime.datetime.now()
        data = base64.b64encode(pickle.dumps(self._kwargs))
        m.append(pack('!H', len(data) + len(self._command) + 1))
        m.append(self._command.encode())
        m.append(b'\n')
        m.append(data)
        return b''.join(m)

    @classmethod
    def unpack(cls, message):
        m = message.decode()
        command, data = m.split("\n")
        kwargs = pickle.loads(base64.b64decode(data))
        return cls(command=command, kwargs=kwargs)

