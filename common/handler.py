class BaseHandler():

    def __init__(self, request):
        self._request = request

    def disconnect(self, user_id, stream):
        raise NotImplementedError()

    def connect(self, user_id, stream):
        raise NotImplementedError()

    def process_request(self):
        raise NotImplementedError()
