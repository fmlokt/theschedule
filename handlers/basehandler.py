# -*- coding: utf-8 -*-

import os
import datetime

import webapp2

from google.appengine.api import users

from objects.group import *


class BaseHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        user = users.get_current_user()
        local_admin = Group.query(Group.group_id ==
                                  kwargs.get('group_id')).get().admin
        self.render_data = {}
        if ('group_id' in kwargs):
            if Group.query(Group.group_id ==
                           kwargs.get('group_id')).get() != None:
                self.render_data['group_id'] = kwargs.get('group_id')
                self.render_data['group_name'] =\
                    Group.query(Group.group_id ==
                                kwargs.get('group_id')).get().name
            else:
                self.error(404)
                self.response.write('404 Not Found\n')
                return
        if user is None:
            self.render_data['login_link'] =\
                users.create_login_url(self.request.uri)
            self.render_data['login_link_text'] = 'Login'
            self.render_data['greeting'] = 'Hello, stranger.'
            self.render_data['is_admin'] = False

        elif users.is_current_user_admin() or (str(user) in str(local_admin)):
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
        self.render_data['group_id'] = kwargs.get('group_id')
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


class BaseLocalAdminHandler(BaseHandler):
    def get(self, *args, **kwargs):
        user = users.get_current_user()
        local_admin = Group.query(Group.group_id ==
                                  kwargs.get('group_id')).get().admin
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            return False
        if not((str(user) in str(local_admin)) or
                users.is_current_user_admin()):
            self.error(403)
            self.response.write('403 Forbidden\n')
            return False
        self.render_data = {}
        self.render_data['group_id'] = kwargs.get('group_id')
        self.render_data['login_link'] =\
            users.create_logout_url(self.request.uri)
        self.render_data['login_link_text'] = 'Logout'
        self.render_data['greeting'] = 'Hello, ' + user.nickname() + '.'
        self.render_data['is_admin'] = True
        return True

    def post(self, *args, **kwargs):
        user = users.get_current_user()
        local_admin = Group.query(Group.group_id ==
                                  kwargs.get('group_id')).get().admin
        if (user is None) or (not ((str(user) in str(local_admin)) or
                                   users.is_current_user_admin())):
            self.error(403)
            self.response.write('403 Forbidden\n')
            return False
        return True
