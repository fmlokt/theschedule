# -*- coding: utf-8 -*-

import os

import jinja2
import webapp2

import environment
from handlers import pairs
from handlers import schedule


application = webapp2.WSGIApplication([
    ('/pairs', pairs.ShowPairs),
    ('/new_pair', pairs.NewPair),
    ('/edit_pair',pairs.EditPair),
    ('/',schedule.ShowSchedule)
], debug=True)