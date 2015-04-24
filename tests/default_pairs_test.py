# -*- coding: utf-8 -*-

import datetime

import unittest2
import webapp2
from google.appengine.ext import testbed

import main
from objects.schedule import DefaultPair


class DefaultPairsTest(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

    @staticmethod
    def make_request(url, method, body=''):
        request = webapp2.Request.blank(url)
        request.method = method
        request.body = body
        return request.get_response(main.application)

    @staticmethod
    def post_default_pair(pair, key=''):
        body = 'classname=' + pair.classname +\
            '&week_day=' + str(pair.week_day) +\
            '&time=' + str(pair.start_time.hour).zfill(2) +\
            ':' + str(pair.start_time.minute).zfill(2) +\
            '&key=' + key
        return DefaultPairsTest.make_request('/default_pairs', 'POST', body)

    def simulate_login(self, user_email='', user_id='', is_admin=False):
        self.testbed.setup_env(
            user_email=user_email,
            user_id=user_id,
            user_is_admin='1' if is_admin else '0',
            overwrite=True)

    def check_default_pair_fields(self, pair1, pair2):
        self.assertEqual(pair1.classname,  pair2.classname)
        self.assertEqual(pair1.week_day,   pair2.week_day)
        self.assertEqual(pair1.start_time, pair2.start_time)

    def test_create_default_pair(self):
        self.simulate_login('a@b.com', '123', True)
        response = DefaultPairsTest.make_request('/new_default_pair', 'GET')
        self.assertEqual(response.status_int, 200)
        pair1 = DefaultPair(classname='Math',
                            week_day=3,
                            start_time=datetime.time(9, 40))
        response = DefaultPairsTest.post_default_pair(pair1)
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.check_default_pair_fields(added_pair, pair1)
        response = DefaultPairsTest.make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        pair2 = DefaultPair(classname='Math 2',
                            week_day=4,
                            start_time=datetime.time(9, 40))
        response = DefaultPairsTest.post_default_pair(pair2)
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(3)
        self.assertEqual(len(pairs_list), 2)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        if added_pair1.classname != pair1.classname:
            swap(added_pair1, added_pair2)
        self.check_default_pair_fields(added_pair1, pair1)
        self.check_default_pair_fields(added_pair2, pair2)
        response = DefaultPairsTest.make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_edit_default_pair(self):
        self.simulate_login('a@b.com', '123', True)
        pair = DefaultPair(classname='Math',
                           week_day=3,
                           start_time=datetime.time(9, 40))
        response = DefaultPairsTest.post_default_pair(pair)
        added_pair = DefaultPair.query().fetch(2)[0]
        response = DefaultPairsTest.make_request('/edit_default_pair?key=' +
                                                 added_pair.key.urlsafe(),
                                                 'GET')
        self.assertEqual(response.status_int, 200)
        pair = DefaultPair(classname='Math 1',
                           week_day=4,
                           start_time=datetime.time(10, 41))
        response = DefaultPairsTest.post_default_pair(pair,
                                                      added_pair.key.urlsafe())
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.check_default_pair_fields(added_pair, pair)
        response = DefaultPairsTest.make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_delete_default_pair(self):
        self.simulate_login('a@b.com', '123', True)
        pair1 = DefaultPair(classname='Math 1',
                            week_day=3,
                            start_time=datetime.time(10, 40))
        pair2 = DefaultPair(classname='Math 2',
                            week_day=3,
                            start_time=datetime.time(9, 40))
        DefaultPairsTest.post_default_pair(pair1)
        DefaultPairsTest.post_default_pair(pair2)
        pairs_list = DefaultPair.query().fetch(2)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        response = DefaultPairsTest.make_request('/delete_pair?key=' +
                                                 added_pair1.key.urlsafe() +
                                                 '&return_url=/default_pairs',
                                                 'GET')
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        remained_pair = pairs_list[0]
        self.assertEqual(remained_pair, added_pair2)

    def test_show_default_pairs(self):
        self.simulate_login('a@b.com', '123', True)
        response = DefaultPairsTest.make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 0)
        pair1 = DefaultPair(classname='Math 1',
                            week_day=3,
                            start_time=datetime.time(10, 40))
        pair2 = DefaultPair(classname='Math 2',
                            week_day=4,
                            start_time=datetime.time(9, 40))
        pair3 = DefaultPair(classname='Math 3',
                            week_day=4,
                            start_time=datetime.time(10, 40))
        DefaultPairsTest.post_default_pair(pair2)
        DefaultPairsTest.post_default_pair(pair3)
        DefaultPairsTest.post_default_pair(pair1)
        response = DefaultPairsTest.make_request('/default_pairs', 'GET')
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
        response = DefaultPairsTest.make_request('/schedule', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 1)
        pair1 = DefaultPair(classname='Math 1',
                            week_day=3,
                            start_time=datetime.time(10, 40))
        pair2 = DefaultPair(classname='Math 2',
                            week_day=4,
                            start_time=datetime.time(9, 40))
        pair3 = DefaultPair(classname='Math 3',
                            week_day=4,
                            start_time=datetime.time(10, 40))
        self.simulate_login('a@b.com', '123', True)
        DefaultPairsTest.post_default_pair(pair2)
        DefaultPairsTest.post_default_pair(pair3)
        DefaultPairsTest.post_default_pair(pair1)
        self.simulate_login()
        response = DefaultPairsTest.make_request('/schedule', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 4)
        self.assertNotEqual(response.body.find('Math 1'), -1)
        self.assertNotEqual(response.body.find('Math 2'), -1)
        self.assertNotEqual(response.body.find('Math 3'), -1)
        self.assertLess(response.body.find('Math 1'),
                        response.body.find('Math 2'))
        self.assertLess(response.body.find('Math 2'),
                        response.body.find('Math 3'))

    def test_all_default_unauth(self):
        response = DefaultPairsTest.make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 302)
        response = DefaultPairsTest.make_request('/new_default_pair', 'GET')
        self.assertEqual(response.status_int, 302)
        pair1 = DefaultPair(classname='Math',
                            week_day=3,
                            start_time=datetime.time(9, 40))
        response = DefaultPairsTest.post_default_pair(pair1)
        self.assertEqual(response.status_int, 403)
        self.simulate_login('a@b.com', '123', True)
        response = DefaultPairsTest.post_default_pair(pair1)
        self.simulate_login()
        pairs_list = DefaultPair.query().fetch(2)
        added_pair = pairs_list[0]
        response = DefaultPairsTest.make_request('/delete_pair?key=' +
                                                 added_pair.key.urlsafe() +
                                                 '&return_url=/default_pairs',
                                                 'GET')
        self.assertEqual(response.status_int, 302)
        response = DefaultPairsTest.make_request('/edit_default_pair?key=' +
                                                 added_pair.key.urlsafe(),
                                                 'GET')
        self.assertEqual(response.status_int, 302)

    def test_all_default_no_admin(self):
        self.simulate_login('c@b.com', '124', False)
        response = DefaultPairsTest.make_request('/default_pairs', 'GET')
        self.assertEqual(response.status_int, 403)
        response = DefaultPairsTest.make_request('/new_default_pair', 'GET')
        self.assertEqual(response.status_int, 403)
        pair1 = DefaultPair(classname='Math',
                            week_day=3,
                            start_time=datetime.time(9, 40))
        response = DefaultPairsTest.post_default_pair(pair1)
        self.assertEqual(response.status_int, 403)
        self.simulate_login('a@b.com', '123', True)
        response = DefaultPairsTest.post_default_pair(pair1)
        self.simulate_login('c@b.com', '124', False)
        pairs_list = DefaultPair.query().fetch(2)
        added_pair = pairs_list[0]
        response = DefaultPairsTest.make_request('/delete_pair?key=' +
                                                 added_pair.key.urlsafe() +
                                                 '&return_url=/default_pairs',
                                                 'GET')
        self.assertEqual(response.status_int, 403)
        response = DefaultPairsTest.make_request('/edit_default_pair?key=' +
                                                 added_pair.key.urlsafe(),
                                                 'GET')
        self.assertEqual(response.status_int, 403)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest2.main()
