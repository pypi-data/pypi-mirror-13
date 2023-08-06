import asyncio
import logging
import sfp

class SfpProtocol(asyncio.Protocol):
    def __init__(self, deliver_callback, asyncio_loop):
        self._context = sfp.Context()
        self.deliver = deliver_callback
        self._loop = asyncio_loop

    def connection_made(self, transport):
        self._transport = transport
        self._context.set_write_callback(self._write)
        self._context.set_deliver_callback(self.__deliver)
        self._context.connect()

    def data_received(self, data):
        for byte in data:
            plen = self._context.deliver(int(byte))

    def write(self, data):
        self._context.write(data)

    def _write(self, data):
        self._transport.write(data)
        return len(data)

    def __deliver(self, bytestring, length):
        '''
        This is a trampoline to self.deliver, since this function will be called
        from C space
        '''
        if length == 0:
            return
        asyncio.run_coroutine_threadsafe(self.deliver(bytestring), self._loop)

