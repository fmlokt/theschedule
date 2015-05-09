# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Group(ndb.Model):
    group_id = ndb.StringProperty()
    name = ndb.StringProperty()
    origin = ndb.StringProperty()
    admin = ndb.StringProperty()
