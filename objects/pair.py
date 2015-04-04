# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

class ScheduledPair(ndb.Model):
	classname = ndb.StringProperty()
	date = ndb.DateProperty()
	start_time = ndb.TimeProperty()
	task = ndb.StringProperty()