from tornado_dnslib.client import RawResolver


import os 
import dnslib

import tornado.testing

# This test uses coroutine style.
class BasicTest(tornado.testing.AsyncTestCase):
    def setUp(self):
        super(BasicTest, self).setUp()


        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.resolver = RawResolver(os.path.join(dir_path, 'files', 'resolv.conf'))
        
    @tornado.testing.gen_test
    def test_basic(self):
        result = yield self.resolver.query(dnslib.DNSRecord.question('wish.com'))
        self.assertTrue(len(result.rr) >= 1)
