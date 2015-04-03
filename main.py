import os

import jinja2
import webapp2

import environment
from handlers import pairs


application = webapp2.WSGIApplication([
    ('/pairs', pairs.ShowPairs),
], debug=True)