# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class DefaultPair(ndb.Model):
    classname = ndb.StringProperty()
    start_time = ndb.TimeProperty()
    week_day = ndb.IntegerProperty()
    group_id = ndb.StringProperty()


class ScheduleSettings(ndb.Model):
    schedule_period = ndb.IntegerProperty()
    first_week_begin = ndb.DateProperty()
    group_id = ndb.StringProperty()
