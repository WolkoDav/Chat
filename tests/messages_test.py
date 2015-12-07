import unittest

from common.messages import Request, Response


class RequestTest(unittest.TestCase):

    def test_pack(self):
        r = Request("LOGIN", kwargs={"username": "test"})
        packing = r.pack()
        self.assertIsInstance(packing, bytes)

    def test_unpack(self):
        message = b"LOGIN\ngAN9cQBYCAAAAHVzZXJuYW1lcQFYBAAAAHRlc3RxAnMu"
        r = Request.unpack(message)
        self.assertEqual(r.command, "LOGIN")
        self.assertIsInstance(r.kwargs, dict)
        self.assertDictEqual(r.kwargs, {'username': "test"})


class ResponseTest(unittest.TestCase):
    def test_pack(self):
        pass

    def test_unpack(self):
        pass