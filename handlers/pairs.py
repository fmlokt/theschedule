# -*- coding: utf-8 -*-

import os
import datetime

import webapp2

from objects.pair import *
from environment import JINJA_ENVIRONMENT


class ShowSchedule(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('templates/schedule.html')
		render_data = { 'days' : [None]*7}
		for day in xrange(7):
			today = datetime.date.today()
			thatday = today + datetime.timedelta(days=day)
			pairs_qry = ScheduledPair.query(ScheduledPair.date == thatday).order(ScheduledPair.start_time)
			render_day = {'week_day' : thatday.strftime('%A'), 'pairs' : [], 'date' : thatday.strftime('%d %B'), 'is_current' : (today == thatday)}
			for pair in pairs_qry:
				render_day['pairs'].append(pair)
			render_data['days'][thatday.weekday()] = render_day
		self.response.write(template.render(render_data))


class ShowPairs(webapp2.RequestHandler):
	def get(self):
		pairs_qry = ScheduledPair.query().order(ScheduledPair.date, ScheduledPair.start_time)
		template = JINJA_ENVIRONMENT.get_template('templates/pairs.html')
		render_data = { 'pairs' : []}
		for pair in pairs_qry:
			pair.edit_link = '/edit_pair?key=' + pair.key.urlsafe()
			render_data['pairs'].append(pair)
		self.response.write(template.render(render_data))
	
	def post(self):
		classname = self.request.get('classname')
		year = int(self.request.get('year'))
		month = int(self.request.get('month'))
		day = int(self.request.get('day'))
		hour = int(self.request.get('hour'))
		minute = int(self.request.get('minute'))
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
			pair = ScheduledPair(classname=classname, date=datetime.date(year, month, day), start_time=datetime.time(hour, minute), task=task)
		pair.put()
		self.redirect('/pairs')


class NewPair(webapp2.RequestHandler):
	def get(self):
		pair = ScheduledPair(classname='classname', date=datetime.date.today(), start_time=datetime.time(9, 10), task='f')
		template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
		render_data = { 'pair' : pair }
		self.response.write(template.render(render_data))


class EditPair(webapp2.RequestHandler):
	def get(self):
		url_key = self.request.get('key')
		key = ndb.Key(urlsafe=url_key)
		pair = key.get()
		template = JINJA_ENVIRONMENT.get_template('templates/edit_pair.html')
		render_data = { 'pair' : pair, 'key_urlsafe' : url_key }
		self.response.write(template.render(render_data))
