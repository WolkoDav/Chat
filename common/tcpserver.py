from tornado import gen
from tornado import tcpserver

__all__ = ['TCPServer', ]


# Сам сервер
class TCPServer(tcpserver.TCPServer):
    """
        Base server for tcp server
    """

    protocol = None
    handler = None
    storage = None

    @gen.coroutine
    def handle_stream(self, stream, address):
        connection = self.protocol(self.handler, stream, self.storage)
        yield connection.on_connect()