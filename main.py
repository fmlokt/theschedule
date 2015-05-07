# -*- coding: utf-8 -*-

import os


import jinja2
import webapp2

import environment
from handlers import pairs
from handlers import schedule
from handlers import crons


application = webapp2.WSGIApplication([
    webapp2.Route(r'/<group_id:[-\w]+>/pairs',
                  handler=pairs.ShowPairs,
                  name='pairs list'),
    webapp2.Route(r'/<group_id:[-\w]+>/new_pair',
                  handler=pairs.NewPair,
                  name='create pair'),
    webapp2.Route(r'/<group_id:[-\w]+>/edit_pair',
                  handler=pairs.EditPair,
                  name='edit pair'),
    webapp2.Route(r'/<group_id:[-\w]+>/',
                  handler=pairs.ShowSchedule,
                  name='schedule'),
    ('/schedule', schedule.ShowDefaultSchedule),
    ('/default_pairs', schedule.ShowDefaultPairs),
    ('/edit_default_pair', schedule.EditDefaultPair),
    ('/new_default_pair', schedule.NewDefaultPair),
    webapp2.Route(r'/<group_id:[-\w]+>/delete_pair',
                  handler=pairs.DeletePair,
                  name='delete pair'),
    ('/copy_from_default', schedule.CopyFromDefault),
    ('/schedule_settings', schedule.EditSettings),
    ('/cron/delete_old', crons.DeleteOld)
], debug=True)
