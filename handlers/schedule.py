# -*- coding: utf-8 -*-

import os
import datetime
import calendar
import re

import webapp2
from google.appengine.api import memcache

from service import timezone
from objects.schedule import *
from environment import JINJA_ENVIRONMENT
from objects.pair import *
from handlers.basehandler import *


DEFAULT_MONDAY = datetime.date(2015, 03, 2)

##\brief Показать стандартное расписание
class ShowDefaultSchedule(BaseHandler):
    def get(self, *args, **kwargs):
        super(ShowDefaultSchedule, self).get(*args, **kwargs)
        group_id = kwargs.get('group_id')
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'default_schedule.html')
        settings_qry = ScheduleSettings.query(DefaultPair.group_id ==
                                              group_id).fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY,
                                        group_id=group_id)
            settings.put()
        else:
            settings = settings_qry[0]
        self.render_data['double_week'] = settings.schedule_period == 14
        self.render_data['odd_days'] = [None] * 6
        for day in xrange(6):
            pairs_qry = DefaultPair.query(DefaultPair.week_day == day,
                                          DefaultPair.group_id == group_id).\
                order(DefaultPair.start_time)
            render_day = {'week_day': day, 'pairs': []}
            for pair in pairs_qry:
                pair.edit_link = '/' + group_id + '/edit_default_pair?key=' + pair.key.urlsafe() +\
                    '&return_url=/' + group_id + '/schedule'
                pair.delete_link = '/' + group_id + '/delete_pair?key=' + pair.key.urlsafe() +\
                    '&return_url=/' + group_id + '/schedule'
                render_day['pairs'].append(pair)
            self.render_data['odd_days'][day] = render_day
        self.render_data['even_days'] = [None] * 6
        for day in xrange(7, 13):
            pairs_qry = DefaultPair.query(DefaultPair.week_day == day,
                                          DefaultPair.group_id == group_id).\
                order(DefaultPair.start_time)
            render_day = {'week_day': day, 'pairs': []}
            for pair in pairs_qry:
                pair.edit_link = '/' + group_id + '/edit_default_pair?key=' + pair.key.urlsafe() +\
                    '&return_url=/' + group_id + '/schedule'
                pair.delete_link = '/' + group_id + '/delete_pair?key=' + pair.key.urlsafe() +\
                    '&return_url=/' + group_id + '/schedule'
                render_day['pairs'].append(pair)
            self.render_data['even_days'][day - 7] = render_day
        self.response.write(template.render(self.render_data))

##\brief Список стандартных пар
class ShowDefaultPairs(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(ShowDefaultPairs, self).get(*args, **kwargs):
            return
        group_id = kwargs.get('group_id')
        pairs_qry = DefaultPair.query(DefaultPair.group_id ==
                                      group_id).order(DefaultPair.week_day,
                                                      DefaultPair.start_time)
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'default_pairs.html')
        self.render_data['pairs'] = []
        for pair in pairs_qry:
            pair.edit_link = '/' + group_id + '/edit_default_pair?key=' +\
                pair.key.urlsafe() + '&return_url=/' +\
                group_id + '/default_pairs'
            pair.delete_link = '/' + group_id + '/delete_pair?key=' +\
                pair.key.urlsafe() + '&return_url=/' +\
                group_id + '/default_pairs'
            self.render_data['pairs'].append(pair)
        self.response.write(template.render(self.render_data))

    def post(self, *args, **kwargs):
        if not super(ShowDefaultPairs, self).post(*args, **kwargs):
            return
        group_id = kwargs.get('group_id')
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
            pair.group_id = group_id
        else:
            pair = DefaultPair(classname=classname, week_day=week_day,
                               start_time=datetime.time(hour, minute),
                               group_id=group_id)
        pair.put()
        return_url = self.request.get('return_url')
        if return_url is None:
            return_url = '/' + group_id + '/default_pairs'
        self.redirect(return_url)


##\brief Создать стандартную пару
class NewDefaultPair(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(NewDefaultPair, self).get(*args, **kwargs):
            return
        group_id = kwargs.get('group_id')
        pair = DefaultPair(classname='classname',
                           week_day=0,
                           group_id=group_id)
        return_url = self.request.get('return_url')
        if return_url is None:
            return_url = '/' + group_id + '/default_pairs'
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'edit_default_pair.html')
        self.render_data['pair'] = pair
        self.render_data['return_url'] = return_url
        self.response.write(template.render(self.render_data))

##\brief Редактировать стандартную пару
class EditDefaultPair(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(EditDefaultPair, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        pair = key.get()
        return_url = self.request.get('return_url')
        if return_url is None:
            return_url = '/' + group_id + '/default_pairs'
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'edit_default_pair.html')
        self.render_data['pair'] = pair
        self.render_data['key_urlsafe'] = url_key
        self.render_data['return_url'] = return_url
        self.response.write(template.render(self.render_data))

##\brief Скопировать из стандартных в ближайшие
class CopyFromDefault(BaseLocalAdminHandler):
    def post(self, *args, **kwargs):
        if not super(CopyFromDefault, self).post(*args, **kwargs):
            return
        group_id = kwargs.get('group_id')
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
        date_begin_new = timezone.today()
        date_end_new = timezone.today() + datetime.timedelta(days=13)
        self.render_data['date_begin'] = str(date_begin_new)
        self.render_data['date_end'] = str(date_end_new)
        template = JINJA_ENVIRONMENT.\
            get_template('templates/copy_from_default.html')
        self.render_data['result'] = [u'Расписание успешно добавлено.']
        if (date_end - date_begin) > 180*datetime.timedelta(days=1):
            self.render_data['result'] = [u'Ошибка: cлишком много дней для копирования.' +\
                                         u' Пожалуйста, попробуйте с меньшим диапазоном.']
            self.response.status = 422
            self.response.write(template.render(self.render_data))
            return
        memcache.delete("schedule_to_render_" + group_id)
        settings_qry = ScheduleSettings.query().fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY)
            settings.put()
        else:
            settings = settings_qry[0]
        while date_begin <= date_end:
            if len(ScheduledPair.query(ScheduledPair.date ==
                   date_begin, ScheduledPair.group_id ==
                   group_id).fetch(1)) == 0:
                weekday = (date_begin - settings.first_week_begin).days %\
                    settings.schedule_period
                pairs_qry = DefaultPair.query(DefaultPair.week_day == weekday,
                                              DefaultPair.group_id == group_id)
                for pair in pairs_qry:
                    new_pair = ScheduledPair(classname=pair.classname,
                                             date=date_begin,
                                             start_time=pair.start_time,
                                             task='',
                                             group_id=group_id)
                    new_pair.put()
            else:
                self.render_data['result'] += [u'Расписание на ' + str(date_begin) +\
                                              u' уже существует.\n']
            date_begin += datetime.timedelta(days=1)
        memcache.delete("schedule_to_render_" + group_id)
        self.response.write(template.render(self.render_data))

    def get(self, *args, **kwargs):
        if not super(CopyFromDefault, self).get(*args, **kwargs):
            return
        date_begin = timezone.today()
        date_end = timezone.today() + datetime.timedelta(days=13)
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'copy_from_default.html')
        self.render_data['date_begin'] = str(date_begin)
        self.render_data['date_end'] = str(date_end)
        self.response.write(template.render(self.render_data))

##\brief Настройки группы
class EditSettings(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(EditSettings, self).get(*args, **kwargs):
            return
        settings_qry = ScheduleSettings.query().fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY,
                                        group_id=kwargs.get('group_id'))
            settings.put()
        else:
            settings = settings_qry[0]
        self.render_data['schedule_period'] = settings.schedule_period
        self.render_data['first_week_begin'] = settings.first_week_begin
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'schedule_settings.html')
        self.response.write(template.render(self.render_data))

    def post(self, *args, **kwargs):
        if not super(EditSettings, self).post(*args, **kwargs):
            return
        date = self.request.get('first_week_begin')
        period = int(self.request.get('schedule_period'))
        reg = '(\d\d\d\d)-(\d\d)-(\d\d)'
        year = int(re.match(reg, date).group(1))
        month = int(re.match(reg, date).group(2))
        day = int(re.match(reg, date).group(3))
        group_id = kwargs.get('group_id')
        settings_qry = ScheduleSettings.query(ScheduleSettings.group_id ==
                                              group_id).fetch(1)
        if len(settings_qry) == 0:
            settings = ScheduleSettings(schedule_period=7,
                                        first_week_begin=DEFAULT_MONDAY,
                                        group_id=group_id)
        else:
            settings = settings_qry[0]
        if period == 14 and settings.schedule_period == 7:
            first_week_qry = DefaultPair.query(DefaultPair.week_day < 7,
                                               DefaultPair.group_id ==
                                               group_id)
            if DefaultPair.query(DefaultPair.week_day > 7,
                                 DefaultPair.group_id ==
                                 group_id).get() is None:
                for pair in first_week_qry:
                    new_pair = DefaultPair(classname=pair.classname,
                                           start_time=pair.start_time,
                                           week_day=pair.week_day + 7,
                                           group_id=pair.group_id)
                    new_pair.put()
        settings.schedule_period = period
        settings.first_week_begin = datetime.date(year, month, day)
        settings.put()
        self.redirect(self.request.uri)
