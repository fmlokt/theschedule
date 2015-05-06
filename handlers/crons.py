# -*- coding: utf-8 -*-

import os
import datetime
import calendar
import re

import webapp2
from google.appengine.api import memcache

from objects.schedule import *
from environment import JINJA_ENVIRONMENT
from objects.pair import *
from handlers.basehandler import *


class DeleteOld(BaseHandler):
    def get(self):
        pairs_qry = ScheduledPair.query(ScheduledPair.date <
                                        datetime.date.today())
        for pair in pairs_qry:
            pair.key.delete()
