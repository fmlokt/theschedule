# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


##\brief Класс группы
class Group(ndb.Model):
    group_id = ndb.StringProperty()
    name = ndb.StringProperty()
    origin = ndb.StringProperty()
    admin = ndb.StringProperty(repeated=True)
    quotes_count = ndb.IntegerProperty(default=0)


##\brief Класс неподтвержденной группы
class Premoderated_Group(ndb.Model):
    group_id = ndb.StringProperty()
    name = ndb.StringProperty()
    origin = ndb.StringProperty()
    admin = ndb.StringProperty(repeated=True)