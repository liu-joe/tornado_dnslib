import udpstream


import time
import struct
import dnslib


import tornado.ioloop
import tornado.gen
import tornado.tcpclient


DEFAULT_RESOLV = '/etc/resolv.conf'
DNS_PORT = 53


class RawResolver(object):
    '''Asynchronous resolver
    An asynchronous dns resolver using tornado iostreams and dnslib
    '''
    def __init__(self, resolv=None, ioloop=None):
        if resolv is None:
            resolv = DEFAULT_RESOLV
        self.resolv = resolv
        
        if ioloop is None:
            ioloop = tornado.ioloop.IOLoop.current()
        self.ioloop = ioloop
        
        self.load_resolv()
        
        self.tcpclient = tornado.tcpclient.TCPClient()

    # TODO: support ports in resolv.conf
    def load_resolv(self):
        servers = []
        with open(self.resolv) as fh:
            for line in fh:
                line = line.strip()
                parts = line.split()
                if parts and parts[0] == 'nameserver':
                    servers.append(parts[1])
        if servers:
            self.servers = servers
        else:
            self.servers = ['127.0.0.1']

    @tornado.gen.coroutine    
    def query(self, q, timeout=1):
        payload = q.pack()
        for server in self.servers:
            try:
                result = yield self._query_server(server, payload, timeout)
            # TODO: be more specific! (need to wrap timeouts etc. into our own timeouts)
            except:
                continue
            raise tornado.gen.Return(result)
            
        raise

    @tornado.gen.coroutine
    def _query_server(self, server, payload, timeout):
        result = yield self._query_server_udp(server, payload, timeout)
        # if it was truncated, do TCP
        if result.header.tc:
            result = yield self._query_server_tcp(server, payload, timeout)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def _query_server_udp(self, server, payload, timeout):
        s = udpstream.UDPStream((server, DNS_PORT), in_ioloop=self.ioloop)
        try:
            s.send(payload)
            data = yield s.read_chunk(timeout=timeout)

            raise tornado.gen.Return(dnslib.DNSRecord.parse(data))
        finally:
            s.close()

    @tornado.gen.coroutine
    def _query_server_tcp(self, server, payload, timeout):
        deadline = self.ioloop.time() + timeout
        def wrap_timeout(f):
            return tornado.gen.with_timeout(deadline, f)
        
        header = struct.pack("!H", len(payload))
        
        s = yield wrap_timeout(self.tcpclient.connect(server, DNS_PORT))
        try:
            # write the entire message (header + payload)
            yield wrap_timeout(s.write(header + payload))
            
            # get the response header (so we know how many bytes to wait for)
            resp_header = yield s.read_bytes(2)
            (l,) = struct.unpack("!H", resp_header)
            
            # wait for the entire response
            data = yield s.read_bytes(l)

            raise tornado.gen.Return(dnslib.DNSRecord.parse(data))
        finally:
            s.close()
