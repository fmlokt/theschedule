# -*- coding: utf-8 -*-

import os
import datetime
import calendar

import webapp2

from objects.schedule import *
from environment import JINJA_ENVIRONMENT
from objects.pair import *


class ShowDefaultSchedule(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'default_schedule.html')
        render_data = {'days': [None] * 7}
        for day in xrange(7):
            pairs_qry = DefaultPair.query(DefaultPair.week_day == day).order(
                DefaultPair.start_time)
            render_day = {'week_day': calendar.day_name[day], 'pairs': []}
            for pair in pairs_qry:
                render_day['pairs'].append(pair)
            render_data['days'][day] = render_day
        self.response.write(template.render(render_data))


class ShowDefaultPairs(webapp2.RequestHandler):
    def get(self):
        pairs_qry = DefaultPair.query().order(DefaultPair.week_day,
                                              DefaultPair.start_time)
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'default_pairs.html')
        render_data = {'pairs': []}
        for pair in pairs_qry:
            pair.edit_link = '/edit_default_pair?key=' + pair.key.urlsafe()
            pair.delete_link = '/delete_pair?key=' + pair.key.urlsafe() +\
                '&return_url=/default_pairs'
            render_data['pairs'].append(pair)
        self.response.write(template.render(render_data))

    def post(self):
        classname = self.request.get('classname')
        week_day = int(self.request.get('week_day'))
        hour = int(self.request.get('hour'))
        minute = int(self.request.get('minute'))
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


class NewDefaultPair(webapp2.RequestHandler):
    def get(self):
        pair = DefaultPair(classname='classname', week_day=0)
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'edit_default_pair.html')
        render_data = {'pair': pair}
        self.response.write(template.render(render_data))


class EditDefaultPair(webapp2.RequestHandler):
    def get(self):
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        pair = key.get()
        template = JINJA_ENVIRONMENT.get_template('templates/'
                                                  'edit_default_pair.html')
        render_data = {'pair': pair, 'key_urlsafe': url_key}
        self.response.write(template.render(render_data))

class CopyFromDefault(webapp2.RequestHandler):
	def get(self):
		year_start = int(self.request.get('year_start'))
		month_start = int(self.request.get('month_start'))
		day_start = int(self.request.get('day_start'))
		year_end = int(self.request.get('year_end'))
		month_end = int(self.request.get('month_end'))
		day_end = int(self.request.get('day_end'))

		date_start = datetime.date(year_start, month_start, day_start)
		date_end = datetime.date(year_end, month_end, day_end)

		while date_start <= date_end:
			weekday = date_start.weekday()
			pairs_qry = DefaultPair.query(DefaultPair.week_day == weekday)
			for pair in pairs_qry:
				new_pair = ScheduledPair(classname=pair.classname, date=date_start, start_time=pair.start_time, task='')
				new_pair.put()
			date_start += datetime.timedelta(days=1)
