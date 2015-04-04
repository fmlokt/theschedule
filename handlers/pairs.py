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
			render_data['pairs'].append(pair)
		self.response.write(template.render(render_data))
	
	def post(self):
		classname = self.request.get('classname')
		year = int(self.request.get('year'))
		month = int(self.request.get('month'))
		date = int(self.request.get('date'))
		hour = int(self.request.get('hour'))
		minute = int(self.request.get('minute'))
		task = self.request.get('task')
		pair = ScheduledPair(classname=classname, date=datetime.date(year, month, date), start_time=datetime.time(hour, minute), task=task)
		pair.put()
