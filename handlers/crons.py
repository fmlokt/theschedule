# -*- coding: utf-8 -*-

import os
import calendar

import webapp2
from google.appengine.api import memcache

from service import timezone
from objects.schedule import *
from environment import JINJA_ENVIRONMENT
from objects.pair import *
from handlers.basehandler import *

##\brief Удаляет старые пары
class DeleteOld(BaseHandler):
    def get(self):
        pairs_qry = ScheduledPair.query(ScheduledPair.date <
                                        timezone.today())
        for pair in pairs_qry:
            pair.key.delete()
