# -*- coding: utf-8 -*-

import os
import datetime

import webapp2

from objects.pair import *
from environment import JINJA_ENVIRONMENT

class ShowSchedule(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('templates/schedule.html')
		render_data = { 'days' : []}
		for day in xrange(7):
			today = datetime.date.today()
			thatday = today + datetime.timedelta(days=day)
			pairs_qry = ScheduledPair.query(ScheduledPair.date == thatday).order(ScheduledPair.start_time)
			render_day = {'week_day' : thatday.strftime('%A'), 'pairs' : [], 'date' : thatday }
			for pair in pairs_qry:
				render_day['pairs'].append(pair)

			render_data['days'].append(render_day)
		self.response.write(template.render(render_data))