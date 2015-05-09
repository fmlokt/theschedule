# -*- coding: utf-8 -*-

import os
import datetime
import re

import webapp2
from google.appengine.api import memcache

from objects.pair import *
from objects.group import *
from environment import JINJA_ENVIRONMENT
from handlers.basehandler import *


class ChooseGroup(BaseHandler):
    def post(self, *args, **kwargs):
        super(ChooseGroup, self).get(*args, **kwargs)
        group_id = self.request.get('group_id')
        group = Group.query(Group.group_id == group_id).fetch(1)
        if len(group) == 0:
            self.response.write('this group id does not exists')
        else:
            self.response.set_cookie('group',
                                     group_id,
                                     expires=datetime.datetime.now() +
                                     datetime.timedelta(days=365))
            self.redirect('/' + group_id + '/')

    def get(self, *args, **kwargs):
        super(ChooseGroup, self).get(*args, **kwargs)
        if 'group' in self.request.cookies:
            self.redirect('/' + self.request.cookies['group'] + '/')
            return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/choose_group.html')
        group_qry = Group.query().order(Group.name)
        self.render_data['groups'] = group_qry
        self.response.write(template.render(self.render_data))


class CreateGroup(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(CreateGroup, self).get(*args, **kwargs):
            return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/create_group.html')
        group = Group(group_id='group',
                      name='',
                      origin='',
                      admin='')
        self.render_data['group'] = group
        self.response.write(template.render(self.render_data))


class ShowGroups(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(ShowGroups, self).get(*args, **kwargs):
            return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/groups.html')
        group_qry = Group.query().order(Group.group_id)
        self.render_data['groups'] = []
        for group in group_qry:
            group.edit_link = '/edit_group?key=' +\
                             group.key.urlsafe()
            group.delete_link = '/delete_group?key=' +\
                group.key.urlsafe() + '&return_url=/groups'
            self.render_data['groups'].append(group)
        self.response.write(template.render(self.render_data))

    def post(self, *args, **kwargs):
        if not super(ShowGroups, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        group_id = self.request.get('group_id')
        name = self.request.get('name')
        origin = self.request.get('origin')
        admin = self.request.get('admin')
        if url_key != '':
            key = ndb.Key(urlsafe=url_key)
            group = key.get()
            group.name = name
            group.origin = origin
            group.group_id = group_id
            group.admin = admin
        else:
            group = Group(group_id=group_id,
                          name=name,
                          origin=origin,
                          admin=admin)
        group.put()
        self.redirect('/groups')


class EditGroup(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(EditGroup, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        group = key.get()
        template = JINJA_ENVIRONMENT.\
            get_template('templates/create_group.html')
        self.render_data['group'] = group
        self.render_data['key_urlsafe'] = url_key
        self.response.write(template.render(self.render_data))


class DeleteGroup(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(DeleteGroup, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        return_url = self.request.get('return_url')
        key = ndb.Key(urlsafe=url_key)
        key.delete()
        self.redirect(return_url)
