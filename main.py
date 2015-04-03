import os
import datetime

import webapp2
import jinja2

from pair import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape']
)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class ShowPairs(webapp2.RequestHandler):
	def get(self):
		pairs_qry = ScheduledPair.query().order(ScheduledPair.date, ScheduledPair.date)
		template = JINJA_ENVIRONMENT.get_template('templates/pair.html')
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
		pair = ScheduledPair(classname=classname, date=datetime.date(year, month, date), start_time=datetime.time(hour, minute))
		pair.put()



application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/pairs', ShowPairs),
], debug=True)