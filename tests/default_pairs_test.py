# -*- coding: utf-8 -*-

import datetime

import unittest2
import webapp2
from google.appengine.ext import testbed

import main
from objects.schedule import DefaultPair
from tests.requests import *


class DefaultPairsTest(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

    def check_default_pair_fields(self, pair1, pair2):
        self.assertEqual(pair1.classname,  pair2.classname)
        self.assertEqual(pair1.week_day,   pair2.week_day)
        self.assertEqual(pair1.start_time, pair2.start_time)

    def test_create_default_pair(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = make_request('/new_default_pair', 'GET')
        self.assertEqual(response.status_int, 200)
        pair1 = DefaultPair(classname='Math', week_day=3,
                            start_time=datetime.time(9, 40))
        response = post_default_pair(pair1)
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.check_default_pair_fields(added_pair, pair1)
        response = make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        pair2 = DefaultPair(classname='Math 2', week_day=4,
                            start_time=datetime.time(9, 40))
        response = post_default_pair(pair2)
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(3)
        self.assertEqual(len(pairs_list), 2)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        if added_pair1.classname != pair1.classname:
            swap(added_pair1, added_pair2)
        self.check_default_pair_fields(added_pair1, pair1)
        self.check_default_pair_fields(added_pair2, pair2)
        response = make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_edit_default_pair(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        pair = DefaultPair(classname='Math', week_day=3,
                           start_time=datetime.time(9, 40))
        response = post_default_pair(pair)
        added_pair = DefaultPair.query().fetch(2)[0]
        response = make_request('/edit_default_pair?key=' +
                                added_pair.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 200)
        pair = DefaultPair(classname='Math 1', week_day=4,
                           start_time=datetime.time(10, 41))
        response = post_default_pair(pair, added_pair.key.urlsafe())
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.check_default_pair_fields(added_pair, pair)
        response = make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_delete_default_pair(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        pair1 = DefaultPair(classname='Math 1', week_day=3,
                            start_time=datetime.time(10, 40))
        pair2 = DefaultPair(classname='Math 2', week_day=3,
                            start_time=datetime.time(9, 40))
        post_default_pair(pair1)
        post_default_pair(pair2)
        pairs_list = DefaultPair.query().fetch(2)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        response = make_request('/delete_pair?key=' +
                                added_pair1.key.urlsafe() +
                                '&return_url=/default_pairs', 'GET')
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        remained_pair = pairs_list[0]
        self.assertEqual(remained_pair, added_pair2)

    def test_show_default_pairs(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 0)
        pair1 = DefaultPair(classname='Math 1', week_day=3,
                            start_time=datetime.time(10, 40))
        pair2 = DefaultPair(classname='Math 2', week_day=4,
                            start_time=datetime.time(9, 40))
        pair3 = DefaultPair(classname='Math 3', week_day=4,
                            start_time=datetime.time(10, 40))
        post_default_pair(pair2)
        post_default_pair(pair3)
        post_default_pair(pair1)
        response = make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 3)
        self.assertNotEqual(response.body.find('Math 1'), -1)
        self.assertNotEqual(response.body.find('Math 2'), -1)
        self.assertNotEqual(response.body.find('Math 3'), -1)
        self.assertLess(response.body.find('Math 1'),
                        response.body.find('Math 2'))
        self.assertLess(response.body.find('Math 2'),
                        response.body.find('Math 3'))

    def test_show_default_schedule(self):
        response = make_request('/schedule', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 1)
        pair1 = DefaultPair(classname='Math 1', week_day=3,
                            start_time=datetime.time(10, 40))
        pair2 = DefaultPair(classname='Math 2', week_day=4,
                            start_time=datetime.time(9, 40))
        pair3 = DefaultPair(classname='Math 3', week_day=4,
                            start_time=datetime.time(10, 40))
        simulate_login(self.testbed, 'a@b.com', '123', True)
        post_default_pair(pair2)
        post_default_pair(pair3)
        post_default_pair(pair1)
        simulate_login(self.testbed)
        response = make_request('/schedule', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('</tr>'), 4)
        self.assertNotEqual(response.body.find('Math 1'), -1)
        self.assertNotEqual(response.body.find('Math 2'), -1)
        self.assertNotEqual(response.body.find('Math 3'), -1)
        self.assertLess(response.body.find('Math 1'),
                        response.body.find('Math 2'))
        self.assertLess(response.body.find('Math 2'),
                        response.body.find('Math 3'))

    def test_all_default_unauth(self):
        response = make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 302)
        response = make_request('/new_default_pair', 'GET')
        self.assertEqual(response.status_int, 302)
        pair1 = DefaultPair(classname='Math', week_day=3,
                            start_time=datetime.time(9, 40))
        response = post_default_pair(pair1)
        self.assertEqual(response.status_int, 403)
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = post_default_pair(pair1)
        simulate_login(self.testbed)
        pairs_list = DefaultPair.query().fetch(2)
        added_pair = pairs_list[0]
        response = make_request('/delete_pair?key=' +
                                added_pair.key.urlsafe() +
                                '&return_url=/default_pairs', 'GET')
        self.assertEqual(response.status_int, 302)
        response = make_request('/edit_default_pair?key=' +
                                added_pair.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 302)

    def test_all_default_no_admin(self):
        simulate_login(self.testbed, 'c@b.com', '124', False)
        response = make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 403)
        response = make_request('/new_default_pair', 'GET')
        self.assertEqual(response.status_int, 403)
        pair1 = DefaultPair(classname='Math', week_day=3,
                            start_time=datetime.time(9, 40))
        response = post_default_pair(pair1)
        self.assertEqual(response.status_int, 403)
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = post_default_pair(pair1)
        simulate_login(self.testbed, 'c@b.com', '124', False)
        pairs_list = DefaultPair.query().fetch(2)
        added_pair = pairs_list[0]
        response = make_request('/delete_pair?key=' +
                                added_pair.key.urlsafe() +
                                '&return_url=/default_pairs', 'GET')
        self.assertEqual(response.status_int, 403)
        response = make_request('/edit_default_pair?key=' +
                                added_pair.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 403)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest2.main()
