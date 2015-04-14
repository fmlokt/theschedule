# -*- coding: utf-8 -*-

import os
import datetime
import calendar

import webapp2

from objects.schedule import *
from environment import JINJA_ENVIRONMENT

class ShowDefaultSchedule(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('templates/default_schedule.html')
		render_data = { 'days' : [None]*7}
		for day in xrange(7):
			pairs_qry = DefaultPair.query(DefaultPair.week_day == day).order(DefaultPair.start_time)
			render_day = {'week_day' : calendar.day_name[day], 'pairs' : []}
			for pair in pairs_qry:
				render_day['pairs'].append(pair)
			render_data['days'][day] = render_day
		self.response.write(template.render(render_data))

class ShowDefaultPairs(webapp2.RequestHandler):
	def get(self):
		pairs_qry = DefaultPair.query().order(DefaultPair.week_day, DefaultPair.start_time)
		template = JINJA_ENVIRONMENT.get_template('templates/default_pairs.html')
		render_data = { 'pairs' : []}
		for pair in pairs_qry:
			pair.edit_link = '/edit_default_pair?key=' + pair.key.urlsafe()
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
			pair = DefaultPair(classname=classname, week_day=week_day, start_time=datetime.time(hour, minute))
		pair.put()
		self.redirect('/default_pairs')


class NewDefaultPair(webapp2.RequestHandler):
	def get(self):
		pair = DefaultPair(classname='classname', week_day=0)
		template = JINJA_ENVIRONMENT.get_template('templates/edit_default_pair.html')
		render_data = { 'pair' : pair }
		self.response.write(template.render(render_data))


class EditDefaultPair(webapp2.RequestHandler):
	def get(self):
		url_key = self.request.get('key')
		key = ndb.Key(urlsafe=url_key)
		pair = key.get()
		template = JINJA_ENVIRONMENT.get_template('templates/edit_default_pair.html')
		render_data = { 'pair' : pair, 'key_urlsafe' : url_key }
		self.response.write(template.render(render_data))
