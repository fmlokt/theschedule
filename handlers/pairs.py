# -*- coding: utf-8 -*-

import os
import datetime
import re

import webapp2
from google.appengine.api import memcache

from handlers.localization import *
from objects.pair import *
from environment import JINJA_ENVIRONMENT
from handlers.basehandler import *


class ShowSchedule(BaseHandler):
    def get(self):
        super(ShowSchedule, self).get()
        template = JINJA_ENVIRONMENT.get_template('templates/schedule.html')
        schedule_to_render = memcache.get("schedule_to_render")
        date_in_memcache = memcache.get("schedule_set_date")
        if (schedule_to_render is None) or (date_in_memcache is None)\
                or (date_in_memcache != datetime.date.today):
            schedule_to_render = [None] * 6
            for day in xrange(7):
                today = datetime.date.today()
                thatday = today + datetime.timedelta(days=day)
                if thatday.weekday() == 6:
                    continue
                pairs_qry = ScheduledPair.query(ScheduledPair.date
                                                == thatday).\
                    order(ScheduledPair.start_time)
                render_day = {'week_day': russian_week(thatday.weekday()),
                              'pairs': [],
                              'date': thatday.strftime('%d') + ' ' +
                              russian_month(thatday.month),
                              'is_current': (today == thatday)}
                for pair in pairs_qry:
                    render_day['pairs'].append(pair)
                schedule_to_render[thatday.weekday()] = render_day
            memcache.set(key="schedule_to_render", value=schedule_to_render)
            memcache.set(key="schedule_set_date", value=datetime.date.today())
        self.render_data['days'] = schedule_to_render
        self.response.write(template.render(self.render_data))


class ShowPairs(BaseAdminHandler):
    def get(self):
        if not super(ShowPairs, self).get():
            return
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
        if not super(ShowPairs, self).post():
            return
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
        replace = bool(self.request.get('replace'))
        if url_key != '':
            key = ndb.Key(urlsafe=url_key)
            pair = key.get()
            pair.classname = classname
            pair.date = datetime.date(year, month, day)
            pair.start_time = datetime.time(hour, minute)
            pair.task = task
            pair.replace = replace
        else:
            pair = ScheduledPair(classname=classname,
                                 date=datetime.date(year, month, day),
                                 start_time=datetime.time(hour, minute),
                                 task=task,
                                 replace=replace)
        pair.put()
        memcache.delete("schedule_to_render")
        self.redirect('/pairs')


class NewPair(BaseAdminHandler):
    def get(self):
        if not super(NewPair, self).get():
            return
        pair = ScheduledPair(classname='classname',
                             date=datetime.date.today(),
                             start_time=datetime.time(9, 10),
                             task='')
        template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
        self.render_data['pair'] = pair
        self.response.write(template.render(self.render_data))


class EditPair(BaseAdminHandler):
    def get(self):
        if not super(EditPair, self).get():
            return
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        pair = key.get()
        template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
        self.render_data['pair'] = pair
        self.render_data['key_urlsafe'] = url_key
        self.response.write(template.render(self.render_data))


class DeletePair(BaseAdminHandler):
    def get(self):
        if not super(DeletePair, self).get():
            return
        url_key = self.request.get('key')
        return_url = self.request.get('return_url')
        key = ndb.Key(urlsafe=url_key)
        key.delete()
        self.redirect(return_url)
