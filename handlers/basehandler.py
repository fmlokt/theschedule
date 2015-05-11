# -*- coding: utf-8 -*-

import os
import datetime

import webapp2

from google.appengine.api import users

from objects.group import *


class BaseHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        user = users.get_current_user()
        local_admin = ''
        self.render_data = {}
        if ('group_id' in kwargs):
            group = Group.query(Group.group_id ==
                                kwargs.get('group_id')).get()
            if group is not None:
                self.render_data['group_id'] = kwargs.get('group_id')
                self.render_data['group_name'] = group.name
                local_admin = group.admin
            else:
                self.error(404)
                self.response.write('404 Not Found\n')
                return False
        self.render_data['is_admin'] = False
        if user is None:
            self.render_data['login_link'] =\
                users.create_login_url(self.request.uri)
            self.render_data['login_link_text'] = u'войти'
            self.render_data['greeting'] = u'Приветствуем, странник.'
        else:
            if users.is_current_user_admin() or\
                    (str(user) in str(local_admin)):
                self.render_data['is_admin'] = True
            self.render_data['login_link'] =\
                users.create_logout_url(self.request.uri)
            self.render_data['login_link_text'] = u'выйти'
            self.render_data['greeting'] = u'Приветствуем, ' +\
                user.nickname() + '.'
        return True


class BaseAdminHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if not super(BaseAdminHandler, self).get(*args, **kwargs):
            return False
        user = users.get_current_user()
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            return False
        if not users.is_current_user_admin():
            self.error(403)
            self.response.write('403 Forbidden\n')
            return False
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
        if not super(BaseLocalAdminHandler, self).get(*args, **kwargs):
            return
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
