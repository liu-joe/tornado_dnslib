import time
import socket
import logging

import tornado.concurrent
import tornado.gen
import tornado.ioloop


class UDPStreamException(Exception):
    pass


class UDPTimeout(UDPStreamException):
    pass



# Based on http://kyle.graehl.org/coding/2012/12/07/tornado-udpstream.html
class UDPStream(object):
    def __init__(self, dest, in_ioloop=None):
        self.dest = dest
        self.socket = None
        self._state = None
        self._read_future = None
        self.ioloop = in_ioloop or tornado.ioloop.IOLoop.instance()
        self.connect()

    def _add_io_state(self, state):
        if self._state is None:
            self._state = tornado.ioloop.IOLoop.ERROR | state
            self.ioloop.add_handler(self.socket, self._handle_events, self._state)
        elif not self._state & state:
            self._state = self._state | state
            self.ioloop.update_handler(self.socket, self._state)

    def connect(self):
        if self.socket:
            raise Exception("wat")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)
        self.socket.connect(self.dest)

    # TODO: handle case where we can't send (send buff is full)
    def send(self,msg):
        return self.socket.send(msg)

    def recv(self,sz):
        return self.socket.recv(sz)

    def close(self):
        self.ioloop.remove_handler(self.socket)
        self.socket.close()
        self.socket = None

    def read_chunk(self, timeout=4):
        # TODO: check that one isn't already outstanding
        self._read_future = tornado.concurrent.Future()
        self._read_timeout = self.ioloop.add_timeout(time.time() + timeout, self._timeout_read, timeout)
        self._add_io_state(self.ioloop.READ)
        return self._read_future

    def _timeout_read(self, timeout):
        if self._read_future:
            self._read_future.set_exception(UDPTimeout("timeout after " + str(timeout)))
            self._read_future = None

    def _handle_read(self):
        if self._read_timeout:
            self.ioloop.remove_timeout(self._read_timeout)
        if self._read_future:
            try:
                data = self.socket.recv(4096)
            except:
                # conn refused??
                data = None
            self._read_future.set_result(data);
            self._read_future = None

    def _handle_events(self, fd, events):
        if events & self.ioloop.READ:
            self._handle_read()
        # if the event is an error, lets tell the socket instead of having it wait for a timeout
        # common one being an ICMP saying that the remote port isn't available
        if events & self.ioloop.ERROR:
            if self._read_timeout:
                self.ioloop.remove_timeout(self._read_timeout)
            if self._read_future:
                self._read_future.set_exception(UDPStreamException("EpollErr"))
