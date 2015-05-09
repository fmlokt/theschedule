# -*- coding: utf-8 -*-


import unittest2
import webapp2
from google.appengine.ext import testbed

import main
from objects.group import Group
from tests.requests import *


class groupsTest(unittest2.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

    def check_group_fields(self, group1, group2):
        self.assertEqual(group1.group_id,   group2.group_id)
        self.assertEqual(group1.name,       group2.name)
        self.assertEqual(group1.origin,     group2.origin)
        self.assertEqual(group1.admin,      group2.admin)

    def test_create_group(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = make_request('/create_group', 'GET')
        self.assertEqual(response.status_int, 200)
        group1 = Group(group_id='group',
                       name='name2',
                       origin='origin1',
                       admin='admin1')
        response = post_group(group1)
        self.assertEqual(response.status_int, 302)
        groups_list = Group.query().fetch()
        self.assertEqual(len(groups_list), 1)
        added_group = groups_list[0]
        self.check_group_fields(added_group, group1)
        response = make_request('/groups', 'GET')
        self.assertEqual(response.status_int, 200)
        group2 = Group(group_id='group2',
                       name='name2',
                       origin='origin2',
                       admin='admin2')
        response = post_group(group2)
        self.assertEqual(response.status_int, 302)
        groups_list = Group.query().fetch(3)
        self.assertEqual(len(groups_list), 2)
        added_group1 = groups_list[0]
        added_group2 = groups_list[1]
        if added_group1.group_id != group1.group_id:
            swap(added_group1, added_group2)
        self.check_group_fields(added_group1, group1)
        self.check_group_fields(added_group2, group2)
        response = make_request('/groups', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_edit_group(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group = Group(group_id='group1',
                      name='name1',
                      origin='origin1',
                      admin='admin1')
        response = post_group(group)
        added_group = Group.query().fetch(2)[0]
        response = make_request('/edit_group?key=' +
                                added_group.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 200)
        group = Group(group_id='group2',
                      name='name2',
                      origin='origin2',
                      admin='admin2')
        response = post_group(group, added_group.key.urlsafe())
        self.assertEqual(response.status_int, 302)
        groups_list = Group.query().fetch(2)
        self.assertEqual(len(groups_list), 1)
        added_group = groups_list[0]
        self.check_group_fields(added_group, group)
        response = make_request('/groups', 'GET')
        self.assertEqual(response.status_int, 200)

    def test_delete_group(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group1 = Group(group_id='group1',
                       name='name1',
                       origin='origin1',
                       admin='admin1')
        group2 = Group(group_id='group2',
                       name='name2',
                       origin='origin2',
                       admin='admin2')
        post_group(group1)
        post_group(group2)
        groups_list = Group.query().fetch(2)
        added_group1 = groups_list[0]
        added_group2 = groups_list[1]
        response = make_request('/delete_group?key=' +
                                added_group1.key.urlsafe() +
                                '&return_url=/groups', 'GET')
        self.assertEqual(response.status_int, 302)
        groups_list = Group.query().fetch(2)
        self.assertEqual(len(groups_list), 1)
        remained_group = groups_list[0]
        self.assertEqual(remained_group, added_group2)

    def test_show_groups(self):
        simulate_login(self.testbed, 'a@b.com', '123', True)
        response = make_request('/groups', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 0)
        group1 = Group(group_id='group1',
                       name='name1',
                       origin='origin1',
                       admin='admin1')
        group2 = Group(group_id='group2',
                       name='name2',
                       origin='origin2',
                       admin='admin2')
        group3 = Group(group_id='group3',
                       name='name3',
                       origin='origin3',
                       admin='admin3')
        post_group(group2)
        post_group(group3)
        post_group(group1)
        response = make_request('/groups', 'GET')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body.count('<tr>'), 3)
        self.assertNotEqual(response.body.find('group1'), -1)
        self.assertNotEqual(response.body.find('group2'), -1)
        self.assertNotEqual(response.body.find('group3'), -1)
        self.assertLess(response.body.find('group1'),
                        response.body.find('group2'))
        self.assertLess(response.body.find('group2'),
                        response.body.find('group3'))

    def test_all_no_admin(self):
        simulate_login(self.testbed, 'c@b.com', '124', False)
        response = make_request('/groups?' +
                                'group_id=group' +
                                '&name=name' +
                                '&origin=origin' +
                                '&admin=admin',
                                'POST')
        self.assertEqual(response.status_int, 403)
        response = make_request('/groups', 'GET')
        self.assertEqual(response.status_int, 403)
        simulate_login(self.testbed, 'a@b.com', '123', True)
        group1 = Group(group_id='group1',
                       name='name1',
                       origin='origin1',
                       admin='admin1')
        post_group(group1)
        groups_list = Group.query().fetch(2)
        added_group1 = groups_list[0]
        simulate_login(self.testbed, 'c@b.com', '124', False)
        response = make_request('/delete_group?key=' +
                                added_group1.key.urlsafe() +
                                '&return_url=/groups', 'GET')
        self.assertEqual(response.status_int, 403)
        groups_list = Group.query().fetch(2)
        self.assertEqual(len(groups_list), 1)
        response = make_request('/edit_group?key=' +
                                added_group1.key.urlsafe(), 'GET')
        self.assertEqual(response.status_int, 403)
        response = make_request('/create_group', 'GET')
        self.assertEqual(response.status_int, 403)
        response = post_group(group1)
        self.assertEqual(response.status_int, 403)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest2.main()
