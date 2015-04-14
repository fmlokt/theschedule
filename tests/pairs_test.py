# -*- coding: utf-8 -*-

import datetime

import unittest2
import webapp2
from google.appengine.ext import testbed

import main
from objects.pair import ScheduledPair


class PairsTest(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def test_create_pair(self):
        pair = ScheduledPair(classname='Math',
                             date=datetime.date(2015, 4, 14),
                             start_time=datetime.time(9, 40),
                             task='some_task')

        request = webapp2.Request.blank('/pairs')
        request.method = 'POST'
        request.body = 'classname=' + pair.classname +\
            '&year=' + str(pair.date.year) +\
            '&month=' + str(pair.date.month) +\
            '&day=' + str(pair.date.day) +\
            '&hour=' + str(pair.start_time.hour) +\
            '&minute=' + str(pair.start_time.minute) + '&task=' + pair.task +\
            '&key='

        response = request.get_response(main.application)
        self.assertEqual(response.status_int, 302)
        pairs_list = ScheduledPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.assertEqual(added_pair.classname, pair.classname)
        self.assertEqual(added_pair.date, pair.date)
        self.assertEqual(added_pair.start_time, pair.start_time)
        self.assertEqual(added_pair.task, pair.task)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest2.main()
