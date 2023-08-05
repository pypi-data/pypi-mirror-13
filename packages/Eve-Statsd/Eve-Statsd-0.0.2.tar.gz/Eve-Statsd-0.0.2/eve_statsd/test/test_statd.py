# -*- coding: utf-8 -*-

import unittest
from eve import Eve
from flask import g
from eve_statsd import StatsD
from statsdmock import StatsdMockServer

settings = {
    'DOMAIN': {
        'foo': {
            'schema': {
                'name': {},
            },
            'resource_methods': ['POST', 'GET'],
        },
    },
}


class TestBase(unittest.TestCase):
    def setUp(self):
        # set up eve
        self.app = Eve(settings=settings)
        self.app.config['TESTING'] = True
        StatsD(self.app)
        self.test_client = self.app.test_client()
        
        # set up statsd mock
        self.server = StatsdMockServer()
        self.server.start()
        
    
    def tearDown(self):
        # Hook
        self.server.stop()
        del self.server
        super(TestBase, self).tearDown()

    def test_counter(self):
        r = self.test_client.get('/foo')
        
        # let's check statsd mock
        self.assertEqual(r.status_code, 200) 
        self.server.wait('foo.counter.get', 1)
        self.server.wait('foo.counter.all', 1)

        data = list(self.server.metrics['foo.counter.get'])
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['value'], '1')
        self.assertEqual(data[0]['type'], 'counter')
        
        data = list(self.server.metrics['foo.counter.all'])
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['value'], '1')
        self.assertEqual(data[0]['type'], 'counter')
        
        self.test_client.get('/foo')
        self.server.wait('foo.counter.get', 2)
        data = list(self.server.metrics['foo.counter.get'])
        self.assertEqual(len(data), 2)
        
    def test_timer(self):
        r = self.test_client.get('/foo')
        
        # let's check statsd mock
        self.assertEqual(r.status_code, 200) 
        self.server.wait('foo.timing.get', 1)

        data = list(self.server.metrics['foo.timing.get'])
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['type'], 'timer')

if __name__ == '__main__':
    unittest.main()