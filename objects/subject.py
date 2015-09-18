# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Subject(ndb.Model):
    group_id = ndb.StringProperty()
    classname = ndb.StringProperty()
    teacher = ndb.StringProperty()
