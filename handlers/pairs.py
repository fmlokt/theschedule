# -*- coding: utf-8 -*-

import os
import re
import json

import webapp2
from google.appengine.api import memcache

from service import timezone
from objects.pair import *
from objects.subject import *
from objects.group import *
from environment import JINJA_ENVIRONMENT
from handlers.basehandler import *


##\brief Показать расписание
class ShowSchedule(BaseHandler):
    def get(self, *args, **kwargs):
        if not super(ShowSchedule, self).get(*args, **kwargs):
            return
        group_id = kwargs.get('group_id')
        template = JINJA_ENVIRONMENT.get_template('templates/schedule.html')
        schedule_to_render = memcache.get("schedule_to_render_" + group_id)
        date_in_memcache = memcache.get("schedule_set_date_" + group_id)
        if (schedule_to_render is None) or (date_in_memcache is None)\
                or (date_in_memcache != timezone.today()):
            schedule_to_render = [None] * 6
            for day in xrange(7):
                today = timezone.today()
                thatday = today + datetime.timedelta(days=day)
                if thatday.weekday() == 6:
                    continue
                pairs_qry = ScheduledPair.query(ScheduledPair.date ==
                                                thatday,
                                                ScheduledPair.group_id ==
                                                group_id).\
                    order(ScheduledPair.start_time)
                render_day = {'week_day': thatday.weekday(),
                              'pairs': [],
                              'date': thatday,
                              'is_current': (today == thatday),
                              'pair_add_link': '/' + group_id +\
                                    '/new_pair?date=' +\
                                    str(thatday) +\
                                    '&return_url=/' + group_id + '/'}
                for pair in pairs_qry:
                    pair_dict = pair.to_dict()
                    pair_dict['edit_link'] = '/' + group_id +\
                         '/edit_pair?key=' +\
                         pair.key.urlsafe() +\
                        '&return_url=/' + group_id + '/'
                    pair_dict['delete_link'] = '/' + group_id +\
                        '/delete_pair?key=' + pair.key.urlsafe() +\
                        '&return_url=/' + group_id + '/'
                    subject = Subject.query(Subject.classname == pair.classname).get()
                    if subject is None:
                        pair_dict['subject_link'] = ''
                    else:
                        pair_dict['subject_link'] = '/' + group_id +\
                            '/subject?key=' + subject.key.urlsafe()
                    render_day['pairs'].append(pair_dict)
                schedule_to_render[thatday.weekday()] = render_day
            memcache.set(key="schedule_to_render_" + group_id,
                         value=schedule_to_render)
            memcache.set(key="schedule_set_date_" + group_id,
                         value=timezone.today())
        self.render_data['days'] = schedule_to_render
        self.response.write(template.render(self.render_data))

##\brief Список пар
class ShowPairs(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        group_id = kwargs.get('group_id')
        if not super(ShowPairs, self).get(*args, **kwargs):
            return
        pairs_qry = ScheduledPair.query(ScheduledPair.group_id ==
                                        group_id).order(ScheduledPair.date,
                                                        ScheduledPair.
                                                        start_time)
        template = JINJA_ENVIRONMENT.get_template('templates/pairs.html')
        self.render_data['pairs'] = []
        for pair in pairs_qry:
            pair.edit_link = '/' + group_id + '/edit_pair?key=' +\
                             pair.key.urlsafe()
            pair.delete_link = '/' + group_id + '/delete_pair?key=' +\
                pair.key.urlsafe() + '&return_url=/' + group_id + '/pairs'
            self.render_data['pairs'].append(pair)
        self.response.write(template.render(self.render_data))

    def post(self, *args, **kwargs):
        if not super(ShowPairs, self).post(*args, **kwargs):
            return
        classname = self.request.get('classname')
        other_classname = self.request.get('other_classname')
        if classname == '':
            classname = other_classname
        date = timezone.datefromstr(self.request.get('date'))
        time = timezone.timefromstr(self.request.get('time'))
        task = self.request.get('task')
        url_key = self.request.get('key')
        replace = bool(self.request.get('replace'))
        group_id = kwargs.get('group_id')
        pair_type = self.request.get('pair_type')
        if url_key != '':
            key = ndb.Key(urlsafe=url_key)
            pair = key.get()
            pair.classname = classname
            pair.date = date
            pair.start_time = time
            pair.task = task
            pair.replace = replace
            pair.group_id = group_id
            pair.pair_type = pair_type
        else:
            pair = ScheduledPair(classname=classname,
                                 date=date,
                                 start_time=time,
                                 task=task,
                                 replace=replace,
                                 group_id=group_id,
                                 pair_type=pair_type)
        pair.put()
        memcache.delete("schedule_to_render_" + group_id)
        return_url = self.request.get('return_url')
        if return_url is None:
            return_url = '/' + group_id + '/pairs'
        self.redirect(return_url)


##\brief Создать пару
class NewPair(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(NewPair, self).get(*args, **kwargs):
            return
        default_day = self.request.get('date')
        if default_day is None or default_day == "":
            default_day = timezone.today()
        else:
            default_day = timezone.datefromstr(default_day)
        pair = ScheduledPair(classname='',
                             date=default_day,
                             start_time=datetime.time(9, 10),
                             replace=True,
                             task='',
                             pair_type='')
        return_url = self.request.get('return_url')
        if return_url is None:
            return_url = '/' + group_id + '/pairs'
        template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
        subjects_qry = Subject.query(Subject.group_id == self.render_data['group_id']).order(Subject.classname)
        self.render_data['subjects'] = subjects_qry
        self.render_data['pair'] = pair
        self.render_data['return_url'] = return_url
        self.response.write(template.render(self.render_data))


##\brief Редактировать пару
class EditPair(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(EditPair, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        pair = key.get()
        return_url = self.request.get('return_url')
        if return_url is None:
            return_url = '/' + group_id + '/pairs'
        template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
        subjects_qry = Subject.query(Subject.group_id == self.render_data['group_id']).order(Subject.classname)
        self.render_data['subjects'] = subjects_qry
        self.render_data['pair'] = pair
        self.render_data['key_urlsafe'] = url_key
        self.render_data['return_url'] = return_url
        self.response.write(template.render(self.render_data))

##\brief Удалить пару
class DeletePair(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(DeletePair, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        group_id = kwargs.get('group_id')
        return_url = self.request.get('return_url')
        if return_url is None:
            return_url = '/' + group_id + '/pairs'
        key = ndb.Key(urlsafe=url_key)
        key.delete()
        memcache.delete("schedule_to_render_" + group_id)
        self.redirect(return_url)

class GetJSON(BaseHandler):
    def get(self, *args, **kwargs):
        group_id = kwargs.get('group_id')
        if not super(GetJSON, self).get(*args, **kwargs):
            return
        pairs_qry = ScheduledPair.query(ScheduledPair.group_id ==
                                        group_id).order(ScheduledPair.date,
                                                        ScheduledPair.
                                                        start_time)
        data={}
        datalist=[]
        for pair in pairs_qry:
            classname = pair.classname
            date = pair.date
            start_time = pair.start_time
            task = pair.task
            replace = pair.replace
            pair_type = pair.pair_type

            data['classname'] = classname
            data['date'] = date.strftime('%d.%m.%y')
            data['start_time'] = start_time.strftime('%H:%M')
            data['task'] = task
            data['replace'] = replace
            data['pair_type'] = pair_type
            datalist.append(data)
        self.response.write(json.dumps(datalist, sort_keys=True, indent=4, separators=(',', ': ')))
        