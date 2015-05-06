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
            self.render_data['is_admin'] = False

        elif users.is_current_user_admin():
            self.render_data['login_link'] =\
                users.create_logout_url(self.request.uri)
            self.render_data['login_link_text'] = 'Logout'
            self.render_data['greeting'] = 'Hello, ' + user.nickname() + '.'
            self.render_data['is_admin'] = True
        else:
            self.render_data['login_link'] =\
                users.create_logout_url(self.request.uri)
            self.render_data['login_link_text'] = 'Logout'
            self.render_data['greeting'] = 'Hello, ' + user.nickname() + '.'
            self.render_data['is_admin'] = False


class BaseAdminHandler(BaseHandler):
    def get(self, *args, **kwargs):
        user = users.get_current_user()
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            return False
        if not users.is_current_user_admin():
            self.error(403)
            self.response.write('403 Forbidden\n')
            return False
        self.render_data = {}
        self.render_data['login_link'] =\
            users.create_logout_url(self.request.uri)
        self.render_data['login_link_text'] = 'Logout'
        self.render_data['greeting'] = 'Hello, ' + user.nickname() + '.'
        self.render_data['is_admin'] = True
        return True

    def post(self, *args, **kwargs):
        user = users.get_current_user()
        if (user is None) or (not users.is_current_user_admin()):
            self.error(403)
            self.response.write('403 Forbidden\n')
            return False
        return True
