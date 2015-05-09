# -*- coding: utf-8 -*-

import datetime

import unittest2
import webapp2
from google.appengine.ext import testbed

import main
from objects.schedule import *
from tests.requests import *


class TwoWeekScheduleTest(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        simulate_login(self.testbed, 'a@b.com', '123', True)

    def check_default_pair_fields(self, pair1, pair2):
        self.assertEqual(pair1.classname,  pair2.classname)
        self.assertEqual(pair1.week_day,   pair2.week_day)
        self.assertEqual(pair1.start_time, pair2.start_time)

    def test_create_2week_default_pair(self):
        group_id = 'asgap'
        response = make_request('/' + group_id + '/new_default_pair', 'GET')
        self.assertEqual(response.status_int, 200)
        pair1 = DefaultPair(classname='Math', week_day=10,
                            start_time=datetime.time(9, 40),
                            group_id=group_id)
        response = post_default_pair(pair1)
        self.assertEqual(response.status_int, 302)
        pairs_list = DefaultPair.query(DefaultPair.group_id ==
                                       group_id).fetch(2)
        self.assertEqual(len(pairs_list), 1)
        added_pair = pairs_list[0]
        self.check_default_pair_fields(added_pair, pair1)

    def test_change_schedule_settings(self):
        group_id = 'asgap'
        response = make_request('/' + group_id + '/schedule_settings', 'GET')
        self.assertEqual(response.status_int, 200)
        settings_qry = ScheduleSettings.query().fetch(2)
        self.assertEqual(len(settings_qry), 1)
        settings = settings_qry[0]
        self.assertEqual(settings.schedule_period, 7)
        self.assertEqual(settings.first_week_begin.weekday(), 0)
        need_settings = ScheduleSettings(schedule_period=14,
                                         first_week_begin=datetime.date(2015,
                                                                        04,
                                                                        20))
        response = make_request('/' + group_id + '/schedule_settings', 'POST',
                                'schedule_period=14'
                                '&first_week_begin=2015-04-20')
        self.assertEqual(response.status_int, 302)
        settings_qry = ScheduleSettings.query().fetch(2)
        self.assertEqual(len(settings_qry), 1)
        settings = settings_qry[0]
        self.assertEqual(settings.schedule_period,
                         need_settings.schedule_period)
        self.assertEqual(settings.first_week_begin,
                         need_settings.first_week_begin)

    def tearDown(self):
        self.testbed.deactivate()
