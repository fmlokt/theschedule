# -*- coding: utf-8 -*-

import datetime

import unittest2
import webapp2
from google.appengine.ext import testbed

import main
from objects.group import Group
from objects.pair import ScheduledPair
from objects.schedule import DefaultPair
from tests.requests import *


class PairsTest(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

    def check_pair_fields(self, pair1, pair2):
        self.assertEqual(pair1.classname,  pair2.classname)
        self.assertEqual(pair1.date,       pair2.date)
        self.assertEqual(pair1.start_time, pair2.start_time)
        self.assertEqual(pair1.task,       pair2.task)

    def test_create_pair(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='a@b.com')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = make_request('/asgap/new_pair', 'GET')
        self.assertEqual(response.status_int, 200)
        pair1 = ScheduledPair(classname='Math',
                              date=datetime.date(2015, 4, 14),
                              start_time=datetime.time(9, 40),
                              task='some task',
                              group_id='asgap')
        response = post_pair(pair1)
        self.assertEqual(response.status_int, 302)
        pairs_list = ScheduledPair.query(ScheduledPair.group_id ==
                                         group_id).fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.check_pair_fields(added_pair, pair1)
        response = make_request('/asgap/pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        pair2 = ScheduledPair(classname='Math 2',
                              date=datetime.date(2015, 4, 15),
                              start_time=datetime.time(9, 40),
                              task='some task',
                              group_id='asgap')
        response = post_pair(pair2)
        self.assertEqual(response.status_int, 302)
        pairs_list = ScheduledPair.query(ScheduledPair.group_id ==
                                         group_id).fetch(3)
        self.assertEqual(len(pairs_list), 2)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        if added_pair1.classname != pair1.classname:
            swap(added_pair1, added_pair2)
        self.check_pair_fields(added_pair1, pair1)
        self.check_pair_fields(added_pair2, pair2)
        response = make_request('/asgap/pairs', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_edit_pair(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='a@b.com')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        simulate_login(self.testbed, 'a@b.com', '123', True)
        pair = ScheduledPair(classname='Math',
                             date=datetime.date(2015, 4, 14),
                             start_time=datetime.time(9, 40),
                             task='some_task',
                             group_id='asgap')
        response = post_pair(pair)
        added_pair = ScheduledPair.query(ScheduledPair.group_id ==
                                         group_id).fetch(2)[0]
        response = make_request('/asgap/edit_pair?key=' +
                                added_pair.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 200)
        pair = ScheduledPair(classname='Math 1',
                             date=datetime.date(2016, 5, 15),
                             start_time=datetime.time(10, 41),
                             task='some task\n1',
                             group_id='asgap')
        response = post_pair(pair, added_pair.key.urlsafe())
        self.assertEqual(response.status_int, 302)
        pairs_list = ScheduledPair.query(ScheduledPair.group_id ==
                                         group_id).fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.check_pair_fields(added_pair, pair)
        response = make_request('/asgap/pairs', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_delete_pair(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='a@b.com')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        simulate_login(self.testbed, 'a@b.com', '123', True)
        pair1 = ScheduledPair(classname='Math 1',
                              date=datetime.date(2015, 4, 14),
                              start_time=datetime.time(10, 40),
                              task='some_task',
                              group_id='asgap')
        pair2 = ScheduledPair(classname='Math 2',
                              date=datetime.date(2015, 4, 15),
                              start_time=datetime.time(9, 40),
                              task='some task',
                              group_id='asgap')
        post_pair(pair1)
        post_pair(pair2)
        pairs_list = ScheduledPair.query(ScheduledPair.group_id ==
                                         group_id).fetch(2)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        response = make_request('/' + group_id + '/delete_pair?key=' +
                                added_pair1.key.urlsafe() +
                                '&return_url=/pairs', 'GET')
        self.assertEqual(response.status_int, 302)
        pairs_list = ScheduledPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        remained_pair = pairs_list[0]
        self.assertEqual(remained_pair, added_pair2)

    def test_show_pairs(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='a@b.com')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = make_request('/' + group_id + '/pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('</tr>'), 1)
        pair1 = ScheduledPair(classname='Math 1',
                              date=datetime.date(2015, 4, 14),
                              start_time=datetime.time(10, 40),
                              task='some task',
                              group_id='asgap')
        pair2 = ScheduledPair(classname='Math 2',
                              date=datetime.date(2015, 4, 15),
                              start_time=datetime.time(9, 40),
                              task='some task',
                              group_id='asgap')
        pair3 = ScheduledPair(classname='Math 3',
                              date=datetime.date(2015, 4, 15),
                              start_time=datetime.time(10, 40),
                              task='some task',
                              group_id='asgap')
        post_pair(pair2)
        post_pair(pair3)
        post_pair(pair1)
        response = make_request('/' + group_id + '/pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('</tr>'), 4)
        self.assertNotEqual(response.body.find('Math 1'), -1)
        self.assertNotEqual(response.body.find('Math 2'), -1)
        self.assertNotEqual(response.body.find('Math 3'), -1)
        self.assertLess(response.body.find('Math 1'),
                        response.body.find('Math 2'))
        self.assertLess(response.body.find('Math 2'),
                        response.body.find('Math 3'))

    def test_show_schedule(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='a@b.com')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        response = make_request('/' + group_id + '/', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('</tr>'), 1)
        if datetime.date.today().weekday() >= 5:
            today = datetime.date.today() + datetime.timedelta(days=2)
        else:
            today = datetime.date.today()
        pair1 = ScheduledPair(classname='Math 1',
                              date=today,
                              start_time=datetime.time(9, 10),
                              task='some task',
                              group_id='asgap')
        pair2 = ScheduledPair(classname='Math 2',
                              date=today,
                              start_time=datetime.time(10, 40),
                              task='some task',
                              group_id='asgap')
        pair3 = ScheduledPair(classname='Math 3',
                              date=today +
                              datetime.timedelta(days=1),
                              start_time=datetime.time(9, 40),
                              task='some task',
                              group_id='asgap')
        simulate_login(self.testbed, 'a@b.com', '123', True)
        post_pair(pair2)
        post_pair(pair3)
        post_pair(pair1)
        simulate_login(self.testbed)
        response = make_request('/' + group_id + '/', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('</tr>'), 4)
        self.assertNotEqual(response.body.find('Math 1'), -1)
        self.assertNotEqual(response.body.find('Math 2'), -1)
        self.assertNotEqual(response.body.find('Math 3'), -1)
        self.assertLess(response.body.find('Math 1'),
                        response.body.find('Math 2'))
        self.assertLess(response.body.find('Math 2'),
                        response.body.find('Math 3'))

    def test_copy_from_default(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='a@b.com')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = make_request('/' + group_id + '/copy_from_default', 'GET')
        self.assertEqual(response.status_int, 200)
        today = datetime.date(2015, 01, 05)
        shift = today + datetime.timedelta(days=6)
        shift_out = today + datetime.timedelta(days=190)
        pair1 = DefaultPair(classname='Math 1',
                            start_time=datetime.time(9, 10),
                            week_day=0,
                            group_id='asgap')
        pair2 = DefaultPair(classname='Math 2',
                            start_time=datetime.time(10, 40),
                            week_day=1,
                            group_id='asgap')
        pair3 = DefaultPair(classname='Math 3',
                            start_time=datetime.time(13, 00),
                            week_day=2,
                            group_id='asgap')
        standard_pair1 = ScheduledPair(classname=pair1.classname,
                                       date=today,
                                       start_time=pair1.start_time,
                                       task='',
                                       group_id='asgap')
        standard_pair2 = ScheduledPair(classname=pair2.classname,
                                       date=today + datetime.timedelta(days=1),
                                       start_time=pair2.start_time,
                                       task='',
                                       group_id='asgap')
        standard_pair3 = ScheduledPair(classname=pair3.classname,
                                       date=today + datetime.timedelta(days=2),
                                       start_time=pair3.start_time,
                                       task='',
                                       group_id='asgap')
        post_default_pair(pair1)
        post_default_pair(pair2)
        post_default_pair(pair3)
        response = make_request('/' + group_id + '/copy_from_default?' +
                                'date_start=' + str(today.year) +
                                '-' + str(today.month).zfill(2) +
                                '-' + str(today.day).zfill(2) +
                                '&date_end=' + str(shift.year) +
                                '-' + str(shift.month).zfill(2) +
                                '-' + str(shift.day).zfill(2),
                                'POST')
        self.assertEqual(response.status_int, 200)
        pairs_list = ScheduledPair.query().order(ScheduledPair.date).fetch(4)
        self.assertEqual(len(pairs_list), 3)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        added_pair3 = pairs_list[2]
        self.check_pair_fields(added_pair1, standard_pair1)
        self.check_pair_fields(added_pair2, standard_pair2)
        self.check_pair_fields(added_pair3, standard_pair3)
        added_pair1.key.delete()
        added_pair2.key.delete()
        added_pair3.key.delete()
        pair4 = DefaultPair(classname='Math 4',
                            start_time=datetime.time(12, 00),
                            week_day=3,
                            group_id='asgap')
        standard_pair4 = ScheduledPair(classname=pair3.classname,
                                       date=today + datetime.timedelta(days=3),
                                       start_time=pair3.start_time,
                                       task='',
                                       group_id='asgap')
        post_pair(standard_pair4)
        post_default_pair(pair4)
        response = make_request('/' + group_id + '/copy_from_default?' +
                                'date_start=' + str(today.year) +
                                '-' + str(today.month).zfill(2) +
                                '-' + str(today.day).zfill(2) +
                                '&date_end=' + str(shift.year) +
                                '-' + str(shift.month).zfill(2) +
                                '-' + str(shift.day).zfill(2),
                                'POST')
        self.assertEqual(response.status_int, 200)
        pairs_list = ScheduledPair.query().order(ScheduledPair.date).fetch(5)
        self.assertEqual(len(pairs_list), 4)
        added_pair1 = pairs_list[0]
        added_pair2 = pairs_list[1]
        added_pair3 = pairs_list[2]
        added_pair4 = pairs_list[3]
        self.check_pair_fields(added_pair1, standard_pair1)
        self.check_pair_fields(added_pair2, standard_pair2)
        self.check_pair_fields(added_pair3, standard_pair3)
        self.check_pair_fields(added_pair4, standard_pair4)
        response = make_request('/' + group_id + '/pairs', 'GET')
        self.assertEqual(response.status_int, 200)
        response = make_request('/' + group_id + '/copy_from_default?' +
                                'date_start=' + str(today.year) +
                                '-' + str(today.month).zfill(2) +
                                '-' + str(today.day).zfill(2) +
                                '&date_end=' + str(shift_out.year) +
                                '-' + str(shift_out.month).zfill(2) +
                                '-' + str(shift_out.day).zfill(2),
                                'POST')
        self.assertEqual(response.status_int, 422)

    def test_all_unauth(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='1')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        today = datetime.date(2015, 01, 05)
        shift = today + datetime.timedelta(days=6)
        response = make_request('/' + group_id + '/copy_from_default?' +
                                'date_start=' + str(today.year) +
                                '-' + str(today.month).zfill(2) +
                                '-' + str(today.day).zfill(2) +
                                '&date_end=' + str(shift.year) +
                                '-' + str(shift.month).zfill(2) +
                                '-' + str(shift.day).zfill(2),
                                'POST')
        self.assertEqual(response.status_int, 403)
        response = make_request('/' + group_id + '/', 'GET')
        self.assertEqual(response.status_int, 200)
        response = make_request('/' + group_id + '/pairs', 'GET')
        self.assertEqual(response.status_int, 302)
        simulate_login(self.testbed, 'a@b.com', '123', True)
        pair1 = ScheduledPair(classname='Math 1',
                              date=datetime.date(2015, 4, 14),
                              start_time=datetime.time(10, 40),
                              task='some_task',
                              group_id='asgap')
        post_pair(pair1)
        pairs_list = ScheduledPair.query().fetch(2)
        added_pair1 = pairs_list[0]
        simulate_login(self.testbed)
        response = make_request('/' + group_id + '/delete_pair?key=' +
                                added_pair1.key.urlsafe() +
                                '&return_url=/pairs', 'GET')
        self.assertEqual(response.status_int, 302)
        pairs_list = ScheduledPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        response = make_request('/' + group_id + '/edit_pair?key=' +
                                added_pair1.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 302)
        response = make_request('/' + group_id + '/new_pair', 'GET')
        self.assertEqual(response.status_int, 302)
        response = post_pair(pair1)
        self.assertEqual(response.status_int, 403)

    def test_all_no_admin(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='asgap', name='1', origin='1', admin='a@b.com')
        post_group(group)
        simulate_login(self.testbed)
        group_id = 'asgap'
        simulate_login(self.testbed, 'c@b.com', '124', False)
        today = datetime.date(2015, 01, 05)
        shift = today + datetime.timedelta(days=6)
        response = make_request('/' + group_id + '/copy_from_default?' +
                                'date_start=' + str(today.year) +
                                '-' + str(today.month).zfill(2) +
                                '-' + str(today.day).zfill(2) +
                                '&date_end=' + str(shift.year) +
                                '-' + str(shift.month).zfill(2) +
                                '-' + str(shift.day).zfill(2),
                                'POST')
        self.assertEqual(response.status_int, 403)
        response = make_request('/' + group_id + '/', 'GET')
        self.assertEqual(response.status_int, 200)
        response = make_request('/' + group_id + '/pairs', 'GET')
        self.assertEqual(response.status_int, 403)
        simulate_login(self.testbed, 'a@b.com', '123', True)
        pair1 = ScheduledPair(classname='Math 1',
                              date=datetime.date(2015, 4, 14),
                              start_time=datetime.time(10, 40),
                              task='some_task',
                              group_id='asgap')
        post_pair(pair1)
        pairs_list = ScheduledPair.query().fetch(2)
        added_pair1 = pairs_list[0]
        simulate_login(self.testbed, 'c@b.com', '124', False)
        response = make_request('/' + group_id + '/delete_pair?key=' +
                                added_pair1.key.urlsafe() +
                                '&return_url=/pairs', 'GET')
        self.assertEqual(response.status_int, 403)
        pairs_list = ScheduledPair.query().fetch(2)
        self.assertEqual(len(pairs_list), 1)
        response = make_request('/' + group_id + '/edit_pair?key=' +
                                added_pair1.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 403)
        response = make_request('/' + group_id + '/new_pair', 'GET')
        self.assertEqual(response.status_int, 403)
        response = post_pair(pair1)
        self.assertEqual(response.status_int, 403)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest2.main()
