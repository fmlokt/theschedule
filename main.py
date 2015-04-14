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
    ('/', pairs.ShowSchedule),
    ('/schedule', schedule.ShowDefaultSchedule),
    ('/default_pairs', schedule.ShowDefaultPairs),
    ('/edit_default_pair', schedule.EditDefaultPair),
    ('/new_default_pair', schedule.NewDefaultPair),
    ('/delete_pair', pairs.DeletePair) 
], debug=True)