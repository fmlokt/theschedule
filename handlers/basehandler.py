# -*- coding: utf-8 -*-

import os
import datetime

import webapp2

from google.appengine.api import users


class BaseHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        user = users.get_current_user()
        self.render_data = {}
        if user is None:
            self.render_data['login_link'] =\
                users.create_login_url(self.request.uri)
            self.render_data['login_link_text'] = 'Login'
            self.render_data['greeting'] = 'Hello, stranger.'
        else:
            self.render_data['login_link'] =\
                users.create_logout_url(self.request.uri)
            self.render_data['login_link_text'] = 'Logout'
            self.render_data['greeting'] = 'Hello, ' + user.nickname() + '.'
