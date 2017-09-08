# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

##\brief Класс цитат
class Quote(ndb.Model):
    group_id = ndb.StringProperty(required=True)
    quote_id = ndb.IntegerProperty(required=True)
    text = ndb.StringProperty(required=True)
    author = ndb.StringProperty()
