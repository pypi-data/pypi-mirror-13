import os
import struct
import json
import importlib
import traceback


CHANNEL_IN = 3
CHANNEL_OUT = 4

HEADER_FMT = '>I'
HEADER_SIZE = struct.calcsize(HEADER_FMT)

HANDSHAKE = {
    'state': 'SUCCESS',
    'version': 1.0
}


def readlen(f, n):
    buffer = bytearray()
    while len(buffer) < n:
        data = f.read(n - len(buffer))
        if data == b'':
            raise EOFError()

        buffer.extend(data)

    return bytes(buffer)


class Runner(object):
    def __init__(self, module):
        self.module = module

        # open channel files
        self.chan_in = os.fdopen(CHANNEL_IN, 'rb')
        self.chan_out = os.fdopen(CHANNEL_OUT, 'wb')

        self.mod = None

    def get_next_call(self):
        header = readlen(self.chan_in, HEADER_SIZE)
        length = struct.unpack(HEADER_FMT, header)[0]

        data = readlen(self.chan_in, length)

        return json.loads(data.decode('utf-8'))

    def send_result(self, result):
        data = json.dumps(result)
        self.chan_out.write(struct.pack(HEADER_FMT, len(data)))
        self.chan_out.write(data.encode())
        self.chan_out.flush()

    def get_module(self):
        if self.mod is None:
            self.mod = importlib.import_module(self.module)

        return self.mod

    def do_call(self, call):
        module = self.get_module()
        func_name = call['function']
        args = call['args'] or []
        kwargs = call['kwargs'] or {}

        result = {}
        try:
            func = getattr(module, func_name)
            call_result = func(*args, **kwargs)
            result = {
                'return': call_result
            }
        except:
            result = {
                'state': 'ERROR',
                'return': traceback.format_exc()
            }

        return result

    def run(self):
        # send handshake
        self.send_result(HANDSHAKE)
        while True:
            result = {'state': 'ERROR'}
            try:
                call = self.get_next_call()
                result = self.do_call(call)
            except EOFError:
                break
            except:
                result['return'] = traceback.format_exc()
            finally:
                self.send_result(result)
