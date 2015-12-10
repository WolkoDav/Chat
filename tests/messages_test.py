import unittest

from common.messages import Message


class RequestTest(unittest.TestCase):

    def test_pack(self):
        r = Message("LOGIN", kwargs={"username": "test"})
        packing = r.pack()
        self.assertIsInstance(packing, bytes)

    def test_unpack(self):
        message = b"LOGIN\ngAN9cQBYCAAAAHVzZXJuYW1lcQFYBAAAAHRlc3RxAnMu"
        r = Message.unpack(message)
        self.assertEqual(r.command, "LOGIN")
        self.assertIsInstance(r.kwargs, dict)
        self.assertDictEqual(r.kwargs, {'username': "test"})