class BaseService():

    def disconnect(self, user_id):
        raise NotImplementedError()

    def login(self, user_id):
        raise NotImplementedError()

    def proccess_request(self, request):
        raise NotImplementedError()
