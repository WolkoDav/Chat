class Message():

    def __init__(self, command, user_id, kwargs):
        self._command = command
        self._user_id = user_id
        self._kwargs = kwargs

    def pack(self):
        raise NotImplementedError()

    @classmethod
    def unpack(cls, message):
        raise NotImplementedError()