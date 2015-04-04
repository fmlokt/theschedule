# -*- coding: utf-8 -*-

import os
import datetime

import webapp2

from objects.pair import *
from environment import JINJA_ENVIRONMENT


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
		print self.request
		classname = self.request.get('classname')
		year = int(self.request.get('year'))
		month = int(self.request.get('month'))
		day = int(self.request.get('day'))
		hour = int(self.request.get('hour'))
		minute = int(self.request.get('minute'))
		task = self.request.get('task')
		url_key = self.request.get('key')
		key = ndb.Key(urlsafe=url_key)
		pair = key.get()
		pair.classname = classname
		pair.date = datetime.date(year, month, day)
		pair.start_time = datetime.time(hour, minute)
		pair.task = task
		#pair = ScheduledPair(classname=classname, date=datetime.date(year, month, day), start_time=datetime.time(hour, minute), task=task)
		pair.put()
		self.redirect('/pairs')


class NewPair(webapp2.RequestHandler):
	def get(self):
		pair = ScheduledPair(classname='classname', date=datetime.date.today(), start_time=datetime.time(9, 10), task='f')
		template = JINJA_ENVIRONMENT.get_template('templates/editpair.html')
		render_data = { 'pair' : pair }
		self.response.write(template.render(render_data))


class EditPair(webapp2.RequestHandler):
	def get(self):
		url_key = self.request.get('key')
		key = ndb.Key(urlsafe=url_key)
		pair = key.get()
		template = JINJA_ENVIRONMENT.get_template('templates/editpair.html')
		render_data = { 'pair' : pair, 'key_urlsafe' : url_key }
		self.response.write(template.render(render_data))
