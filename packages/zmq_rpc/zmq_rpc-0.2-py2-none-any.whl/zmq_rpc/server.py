# -*- encoding: utf-8 -*-

import zmq
import struct
import logging
import os
import random
import sys
import time
from base import ZmqRpcConnector


logger = logging.getLogger(__name__)
log = logger.debug


class RpcMethod(object):
    """Decorator to mark a function as a RPC method, and optionally give it
    a name that can include periods and Unicode characters.
    Use: @RpcMethod or @RpcMethod(name)
    """

    def __new__(cls, name_or_func=None):
        if name_or_func is not None and hasattr(name_or_func, '__call__'):
            new = super(RpcMethod, cls).__new__(cls, None)
            new.__init__()
            return new.__call__(name_or_func)
        else:
            new = super(RpcMethod, cls).__new__(cls, name_or_func)
            return new

    def __init__(self, name=None):
        self.name = name

    def __call__(self, func):
        name = self.name if self.name is not None else func.__name__
        func.__rpc__ = name
        return func


class ZmqRpcServerMeta(type):
    """Add all methods that have been marked as RPC in the class definition
    (with the :class:`RpcMethod` decorator) to the class' RPC interface.
    """

    def __init__(cls, name, bases, nmspc):

        if '_methods' not in nmspc:
            cls._methods = nmspc['_methods'] = {}
        for attr, value in nmspc.iteritems():
            rpc_name = getattr(value, '__rpc__', None)
            if rpc_name:
                cls._methods[rpc_name] = getattr(cls, attr)

        super(ZmqRpcServerMeta, cls).__init__(name, bases, nmspc)


class ZmqRpcServer(ZmqRpcConnector):
    """zmq-rpc server implementation with pyzmq.
    """

    __metaclass__ = ZmqRpcServerMeta
    _methods = {}

    REQ = struct.Struct('=HHLd')
    RESP_PREFIX = struct.Struct('=HH')
    RESP_SUFFIX = struct.Struct('=Ld?')

    def __init__(self, url):
        """Initialize the connector.
        :param url: URL for the aiozmq server.
        """

        super(ZmqRpcServer, self).__init__()

        self.prefix = self.RESP_PREFIX.pack(os.getpid() % 0x10000,
                                            random.randrange(0x10000))
        self.running = False

        # Open a regular 0mq connection, in "dealer" mode.
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(url)

    def rpc_call(self, data):
        """Interpret the received data to call the specified method and
        return its result.

        :param: data: the RPC function call sent by a client.
        :type: data: list

        :return: The formatted result of the RPC function call.
        """
        try:
            pre = data[:-4]
            header, bname, bargs, bkwargs = data[-4:]
            pid, rnd, req_id, timestamp = self.REQ.unpack(header)

            name = bname.decode('utf-8')
            args = self.packer.unpack(bargs)
            kwargs = self.packer.unpack(bkwargs)
        except Exception as exc:
            logger.critical("Cannot unpack %r", data, exc_info=sys.exc_info())
            return
        try:
            func = self._methods[name]
            res = func(self, *args, **kwargs)
            return self.rpc_result(res, req_id, pre, False)
        except Exception as exc:
            exc_info = (
                exc.__class__.__module__ + '.' + exc.__class__.__name__,
                exc.args, repr(exc)
            )
            return self.rpc_result(exc_info, req_id, pre, True)

    def rpc_result(self, ret, req_id, pre, exc):
        """Format the result as a RPC call reply.

        :param: ret: the return value of the RPC call.

        :param: req_id: the identifier of the request.
        :type: req_id: list

        :param: pre: the unchanged prefixes from the request.
        :type: pre: list

        :param: exc: whether the result signals an exception.
        :type: exc: bool

        :return: The formatted result of the RPC function call.
        """
        prefix = self.prefix + self.RESP_SUFFIX.pack(req_id, time.time(), exc)
        return pre + [prefix, self.packer.pack(ret)]

    def run(self):
        """Start the server execution loop.
        """

        self.running = True
        while self.running:
            data = self.receive()
            reply = self.rpc_call(data)
            self.send(reply)

    def stop(self):
        """Stop the execution loop after the current RPC call has been treated.
        """
        self.running = False


def main():
    """Start a test server.
    """

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )

    class AddServer(ZmqRpcServer):
        @RpcMethod
        def test_func(self, a, b):
            self.stop()
            return a + b

    log('start')

    zmq_rpc_server = AddServer('tcp://*:2678')
    zmq_rpc_server.run()

    log('done')


if __name__ == '__main__':
    main()
