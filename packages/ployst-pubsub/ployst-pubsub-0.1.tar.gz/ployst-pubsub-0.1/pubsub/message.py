import json
from base64 import b64encode, b64decode


def encode(payload):
    payload = json.dumps(payload).encode('utf-8')
    return b64encode(payload).decode('ascii')


def decode(payload):
    payload = b64decode(payload.encode('ascii'))
    return json.loads(payload.decode('utf-8'))


class ReceivedMessage(dict):

    def __init__(self, data, ack_callback):
        super().__init__(data)
        self.acknowledge = ack_callback

    def ack(self):
        self.acknowledge([self])

    @property
    def payload(self):
        return decode(self['message']['data'])
