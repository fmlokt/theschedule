# -*- coding: utf-8 -*-

import os
import datetime
import re

import webapp2

from objects.pair import *
from environment import JINJA_ENVIRONMENT
from handlers.basehandler import BaseHandler


class ShowSchedule(BaseHandler):
    def get(self):
        super(ShowSchedule, self).get()
        template = JINJA_ENVIRONMENT.get_template('templates/schedule.html')
        self.render_data['days'] = [None] * 7
        for day in xrange(7):
            today = datetime.date.today()
            thatday = today + datetime.timedelta(days=day)
            pairs_qry = ScheduledPair.query(ScheduledPair.date == thatday).\
                order(ScheduledPair.start_time)
            render_day = {'week_day': thatday.strftime('%A'), 'pairs': [],
                          'date': thatday.strftime('%d %B'),
                          'is_current': (today == thatday)}
            for pair in pairs_qry:
                render_day['pairs'].append(pair)
            self.render_data['days'][thatday.weekday()] = render_day
        self.response.write(template.render(self.render_data))


class ShowPairs(BaseHandler):
    def get(self):
        super(ShowPairs, self).get()
        pairs_qry = ScheduledPair.query().order(ScheduledPair.date,
                                                ScheduledPair.start_time)
        template = JINJA_ENVIRONMENT.get_template('templates/pairs.html')
        self.render_data['pairs'] = []
        for pair in pairs_qry:
            pair.edit_link = '/edit_pair?key=' + pair.key.urlsafe()
            pair.delete_link = '/delete_pair?key=' + pair.key.urlsafe() +\
                '&return_url=/pairs'
            self.render_data['pairs'].append(pair)
        self.response.write(template.render(self.render_data))

    def post(self):
        classname = self.request.get('classname')
        date = str(self.request.get('date'))
        reg_date = '(\d\d\d\d)-(\d\d)-(\d\d)'
        year = int(re.match(reg_date, date).group(1))
        month = int(re.match(reg_date, date).group(2))
        day = int(re.match(reg_date, date).group(3))
        time = str(self.request.get('time'))
        reg_time = '(\d\d):(\d\d)'
        hour = int(re.match(reg_time, time).group(1))
        minute = int(re.match(reg_time, time).group(2))
        task = self.request.get('task')
        url_key = self.request.get('key')
        if url_key != '':
            key = ndb.Key(urlsafe=url_key)
            pair = key.get()
            pair.classname = classname
            pair.date = datetime.date(year, month, day)
            pair.start_time = datetime.time(hour, minute)
            pair.task = task
        else:
            pair = ScheduledPair(classname=classname,
                                 date=datetime.date(year, month, day),
                                 start_time=datetime.time(hour, minute),
                                 task=task)
        pair.put()
        self.redirect('/pairs')


class NewPair(BaseHandler):
    def get(self):
        super(NewPair, self).get()
        pair = ScheduledPair(classname='classname',
                             date=datetime.date.today(),
                             start_time=datetime.time(9, 10),
                             task='')
        template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
        self.render_data['pair'] = pair
        self.response.write(template.render(self.render_data))


class EditPair(BaseHandler):
    def get(self):
        super(EditPair, self).get()
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        pair = key.get()
        template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
        self.render_data['pair'] = pair
        self.render_data['key_urlsafe'] = url_key
        self.response.write(template.render(self.render_data))


class DeletePair(webapp2.RequestHandler):
    def get(self):
        url_key = self.request.get('key')
        return_url = self.request.get('return_url')
        key = ndb.Key(urlsafe=url_key)
        key.delete()
        self.redirect(return_url)
