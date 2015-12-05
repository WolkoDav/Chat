import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from tornado import options
from tornado import ioloop

from common.protocol import BaseProtocol
from common.tcpserver import TCPServer
from common.service import BaseService

options.define("address", default="127.0.0.1", help="HOST", group="listen")
options.define("port", type=int, default=8888, help="PORT", group="listen")
options.options.parse_command_line()


class ChatService(BaseService):
    pass


class Protocol(BaseProtocol):
    service = ChatService()


class ChatServer(TCPServer):
    protocol = Protocol


if __name__ == "__main__":
    server = ChatServer()
    server.listen(**options.options.group_dict("listen"))
    ioloop.IOLoop.current().start()