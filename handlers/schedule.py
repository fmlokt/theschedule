# -*- coding: utf-8 -*-

import os
import datetime
import calendar

import webapp2
import re

from objects.schedule import *
from environment import JINJA_ENVIRONMENT
from objects.pair import *
from handlers.basehandler import *


DEFAULT_MONDAY = datetime.date(2015, 03, 2)


class ShowDefaultSchedule(BaseHandler):
    def get(self):
        super(ShowDefaultSchedule, self).get()
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'default_schedule.html')
        settings_qry = ScheduleSettings.query().fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY)
            settings.put()
        else:
            settings = settings_qry[0]
        self.render_data['double_week'] = settings.schedule_period == 14
        self.render_data['odd_days'] = [None] * 6
        for day in xrange(6):
            pairs_qry = DefaultPair.query(DefaultPair.week_day == day).order(
                DefaultPair.start_time)
            render_day = {'week_day': calendar.day_name[day], 'pairs': []}
            for pair in pairs_qry:
                render_day['pairs'].append(pair)
            self.render_data['odd_days'][day] = render_day
        self.render_data['even_days'] = [None] * 6
        for day in xrange(7, 13):
            pairs_qry = DefaultPair.query(DefaultPair.week_day == day).order(
                DefaultPair.start_time)
            render_day = {'week_day': calendar.day_name[day - 7], 'pairs': []}
            for pair in pairs_qry:
                render_day['pairs'].append(pair)
            self.render_data['even_days'][day - 7] = render_day
        self.response.write(template.render(self.render_data))


class ShowDefaultPairs(BaseAdminHandler):
    def get(self):
        if not super(ShowDefaultPairs, self).get():
            return
        pairs_qry = DefaultPair.query().order(DefaultPair.week_day,
                                              DefaultPair.start_time)
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'default_pairs.html')
        self.render_data['pairs'] = []
        for pair in pairs_qry:
            pair.edit_link = '/edit_default_pair?key=' + pair.key.urlsafe()
            pair.delete_link = '/delete_pair?key=' + pair.key.urlsafe() +\
                '&return_url=/default_pairs'
            self.render_data['pairs'].append(pair)
        self.response.write(template.render(self.render_data))

    def post(self):
        if not super(ShowDefaultPairs, self).post():
            return
        classname = self.request.get('classname')
        week_day = int(self.request.get('week_day')) +\
            7 * int(self.request.get('week_parity'))
        time = str(self.request.get('time'))
        reg_time = '(\d\d):(\d\d)'
        hour = int(re.match(reg_time, time).group(1))
        minute = int(re.match(reg_time, time).group(2))
        url_key = self.request.get('key')
        if url_key != '':
            key = ndb.Key(urlsafe=url_key)
            pair = key.get()
            pair.classname = classname
            pair.week_day = week_day
            pair.start_time = datetime.time(hour, minute)
        else:
            pair = DefaultPair(classname=classname, week_day=week_day,
                               start_time=datetime.time(hour, minute))
        pair.put()
        self.redirect('/default_pairs')


class NewDefaultPair(BaseAdminHandler):
    def get(self):
        if not super(NewDefaultPair, self).get():
            return
        pair = DefaultPair(classname='classname', week_day=0)
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'edit_default_pair.html')
        self.render_data['pair'] = pair
        self.response.write(template.render(self.render_data))


class EditDefaultPair(BaseAdminHandler):
    def get(self):
        if not super(EditDefaultPair, self).get():
            return
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        pair = key.get()
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'edit_default_pair.html')
        self.render_data['pair'] = pair
        self.render_data['key_urlsafe'] = url_key
        self.response.write(template.render(self.render_data))


class CopyFromDefault(BaseAdminHandler):
    def post(self):
        if not super(CopyFromDefault, self).post():
            return
        date_start = str(self.request.get('date_start'))
        date_finish = str(self.request.get('date_end'))
        reg = '(\d\d\d\d)-(\d\d)-(\d\d)'
        year_start = int(re.match(reg, date_start).group(1))
        month_start = int(re.match(reg, date_start).group(2))
        day_start = int(re.match(reg, date_start).group(3))
        year_end = int(re.match(reg, date_finish).group(1))
        month_end = int(re.match(reg, date_finish).group(2))
        day_end = int(re.match(reg, date_finish).group(3))

        date_begin = datetime.date(year_start, month_start, day_start)
        date_end = datetime.date(year_end, month_end, day_end)
        if (date_end - date_begin) > 180*datetime.timedelta(days=1):
            self.response.write('Too many days to copy')
            self.response.status = 422
            return
        settings_qry = ScheduleSettings.query().fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY)
            settings.put()
        else:
            settings = settings_qry[0]
        while date_begin <= date_end:
            if len(ScheduledPair.query(ScheduledPair.date ==
                   date_begin).fetch(1)) == 0:
                weekday = (date_begin - settings.first_week_begin).days %\
                    settings.schedule_period
                pairs_qry = DefaultPair.query(DefaultPair.week_day == weekday)
                for pair in pairs_qry:
                    new_pair = ScheduledPair(classname=pair.classname,
                                             date=date_begin,
                                             start_time=pair.start_time,
                                             task='')
                    new_pair.put()
            else:
                self.response.write('Schedule for ' + str(date_begin) +
                                    ' already exists\n')
            date_begin += datetime.timedelta(days=1)

    def get(self):
        if not super(CopyFromDefault, self).get():
            return
        date_begin = datetime.date.today()
        date_end = datetime.date.today() + datetime.timedelta(days=13)
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'copy_from_default.html')
        self.render_data['date_begin'] = str(date_begin)
        self.render_data['date_end'] = str(date_end)
        self.response.write(template.render(self.render_data))


class EditSettings(BaseAdminHandler):
    def get(self):
        if not super(EditSettings, self).get():
            return
        settings_qry = ScheduleSettings.query().fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY)
            settings.put()
        else:
            settings = settings_qry[0]
        self.render_data['schedule_period'] = settings.schedule_period
        self.render_data['first_week_begin'] = settings.first_week_begin
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'schedule_settings.html')
        self.response.write(template.render(self.render_data))

    def post(self):
        if not super(EditSettings, self).post():
            return
        date = self.request.get('first_week_begin')
        period = int(self.request.get('schedule_period'))
        reg = '(\d\d\d\d)-(\d\d)-(\d\d)'
        year = int(re.match(reg, date).group(1))
        month = int(re.match(reg, date).group(2))
        day = int(re.match(reg, date).group(3))
        settings_qry = ScheduleSettings.query().fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY)
        else:
            settings = settings_qry[0]
        settings.schedule_period = period
        settings.first_week_begin = datetime.date(year, month, day)
        settings.put()
        self.redirect(self.request.uri)
