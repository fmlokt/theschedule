# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

##\brief Класс пар
class ScheduledPair(ndb.Model):
    classname = ndb.StringProperty()
    date = ndb.DateProperty()
    start_time = ndb.TimeProperty()
    duration = ndb.IntegerProperty()
    task = ndb.StringProperty()
    replace = ndb.BooleanProperty()
    group_id = ndb.StringProperty()
    pair_type = ndb.StringProperty()
