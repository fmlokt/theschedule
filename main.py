import webapp2
import datetime

from pair import *

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class ShowPairs(webapp2.RequestHandler):
	def get(self):
		pairs_qry = ScheduledPair.query().order(ScheduledPair.date, ScheduledPair.date)
		self.response.write('<html>\n<head>\n<title>Scheduled pairs</title>\n</head>\n<body>\n')
		self.response.write('<table border=3 column=3>\n')
		for pair in pairs_qry:
			self.response.write('<tr><td>{}</td><td>{}</td><td>{}</td></tr>\n'.format(pair.classname, str(pair.date), str(pair.start_time)))
		self.response.write('</table>\n</body>\n</html>\n')
	
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