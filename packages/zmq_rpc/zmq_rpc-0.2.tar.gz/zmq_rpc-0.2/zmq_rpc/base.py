"""zmq-rpc implementation with pyzmq.
This file contains stuff common to both the client and the server.
"""

from packer import Packer


class ZmqRpcConnector(object):
    """Base class for zmq-rpc client & server implementations with pyzmq.
    """

    def __init__(self):
        self.packer = Packer()

    def send(self, data):
        """Send data to the connected peer.
        :type data: List.
        """

        # Send the data as multipart (that is what aiozmq uses).
        return self.socket.send_multipart(data)

    def receive(self):
        """Receive data sent by the connected peer.
        :rtype: List.
        """

        # Receive the data as multipart (that is what aiozmq uses).
        return self.socket.recv_multipart()
