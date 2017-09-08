# -*- coding: utf-8 -*-

import webapp2

import main


def simulate_login(testbed, user_email='', user_id='', is_admin=False):
    testbed.setup_env(user_email=user_email, user_id=user_id,
                      user_is_admin='1' if is_admin else '0', overwrite=True)


def make_request(url, method, body=''):
    request = webapp2.Request.blank(url)
    request.method = method
    request.body = body
    return request.get_response(main.application)


def post_pair(pair, key=''):
    body = 'classname=' + pair.classname +\
        '&date=' + str(pair.date.year) +\
        '-' + str(pair.date.month).zfill(2) +\
        '-' + str(pair.date.day).zfill(2) +\
        '&time=' + str(pair.start_time.hour).zfill(2) +\
        ':' + str(pair.start_time.minute).zfill(2) + '&duration=' +\
        str(pair.duration) + '&task=' +\
        pair.task + '&key=' + key + '&group_id' + str(pair.group_id)
    return make_request('/' + str(pair.group_id) + '/pairs', 'POST', body)


def post_default_pair(pair, key=''):
    body = 'classname=' + pair.classname +\
        '&week_day=' + str(pair.week_day % 7) +\
        '&week_parity=' + str(pair.week_day / 7) +\
        '&time=' + str(pair.start_time.hour).zfill(2) +\
        ':' + str(pair.start_time.minute).zfill(2) +\
        '&duration=' + str(pair.duration) +\
        '&key=' + key + '&group_id' + str(pair.group_id)
    return make_request('/' + str(pair.group_id) +
                        '/default_pairs', 'POST', body)


def post_group(group, key=''):
    body = 'group_id=' + str(group.group_id) +\
        '&name=' + str(group.name) + '&origin=' + str(group.origin) +\
        '&admin=' + str(group.admin[0]) + '&key=' + key
    return make_request('/groups', 'POST', body)
