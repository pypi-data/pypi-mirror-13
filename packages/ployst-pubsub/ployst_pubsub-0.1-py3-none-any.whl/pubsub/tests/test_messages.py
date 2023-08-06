# -*- coding: utf-8 -*-
from unittest import TestCase

from pubsub.message import encode, decode


class TestMessage(TestCase):

    def test_encoded_messages_are_decoded_correctly(self):
        def encode_decode(message):
            return decode(encode(message))

        for message in ['hello', 'Barrobés', 12, {'too': True}]:
            self.assertEqual(message, encode_decode(message))
