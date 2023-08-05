"""Message serialization (messagepack by default).
"""

import msgpack


class Packer(object):
    def pack(self, data):
        return msgpack.packb(data, encoding='utf-8', use_bin_type=True)

    def unpack(self, data):
        return msgpack.unpackb(data, encoding='utf-8', use_list=False)
