# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class DefaultPair(ndb.Model):
    classname = ndb.StringProperty()
    start_time = ndb.TimeProperty()
    week_day = ndb.IntegerProperty()
