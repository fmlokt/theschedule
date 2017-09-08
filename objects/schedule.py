# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

##\brief Класс стандартных пар
class DefaultPair(ndb.Model):
    classname = ndb.StringProperty()
    start_time = ndb.TimeProperty()
    duration = ndb.IntegerProperty()
    week_day = ndb.IntegerProperty()
    group_id = ndb.StringProperty()
    pair_type = ndb.StringProperty()

##\brief Класс настроек группы
class ScheduleSettings(ndb.Model):
    schedule_period = ndb.IntegerProperty()
    first_week_begin = ndb.DateProperty()
    group_id = ndb.StringProperty()
