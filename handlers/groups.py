# -*- coding: utf-8 -*-

import os
import datetime
import re

import webapp2
from google.appengine.api import memcache
from google.appengine.api import mail

from objects.pair import *
from objects.group import *
from environment import JINJA_ENVIRONMENT
from handlers.basehandler import *

##\brief Выбор группы
class ChooseGroup(BaseHandler):
    def post(self, *args, **kwargs):
        group_id = self.request.get('group_id')
        group = Group.query(Group.group_id == group_id).get()
        if group is None:
            self.response.write('this group id does not exists')
        else:
            self.response.set_cookie('group',
                                     group_id,
                                     expires=datetime.datetime.now() +
                                     datetime.timedelta(days=365))
            self.redirect('/' + group_id + '/')

    def get(self, *args, **kwargs):
        super(ChooseGroup, self).get(*args, **kwargs)
        print 'GROUP FLAG : ' + str(self.request.get('change_group'))
        if (not self.request.get('change_group') == 'True') and\
                ('group' in self.request.cookies):
            if Group.query(Group.group_id == self.request.cookies['group']).get() is not None:
                self.redirect('/' + self.request.cookies['group'] + '/')
                return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/choose_group.html')
        group_qry = Group.query().order(Group.name)
        self.render_data['groups'] = group_qry
        self.response.write(template.render(self.render_data))

##\brief Создать группу
class CreateGroup(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(CreateGroup, self).get(*args, **kwargs):
            return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/create_group.html')
        group = Group(group_id='group',
                      name='',
                      origin='',
                      admin=[])
        self.render_data['group'] = group
        self.response.write(template.render(self.render_data))

##\brief Показать список групп
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
        if not super(ShowGroups, self).post(*args, **kwargs):
            return
        url_key = self.request.get('key')
        group_id = self.request.get('group_id')
        name = self.request.get('name')
        origin = self.request.get('origin')
        admin_raw = self.request.get('admin').lower()
        admin = re.split(';| |,|\*|\n',admin_raw)
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

##\brief Редактировать группу
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

##\brief Удалить группу
class DeleteGroup(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(DeleteGroup, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        return_url = self.request.get('return_url')
        key = ndb.Key(urlsafe=url_key)
        key.delete()
        self.redirect(return_url)

class ShowRequests(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(ShowRequests, self).get(*args, **kwargs):
            return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/groups_requests.html')
        group_qry = Premoderated_Group.query().order(Premoderated_Group.group_id)
        self.render_data['groups'] = []
        for group in group_qry:
            group.edit_link = '/edit_group?key=' +\
                             group.key.urlsafe()
            group.delete_link = '/delete_group?key=' +\
                group.key.urlsafe() + '&return_url=/groups'
            group.apply_link = '/apply_request?key=' +\
                group.key.urlsafe() + '&return_url=/groups'
            self.render_data['groups'].append(group)
        self.response.write(template.render(self.render_data))

class ApplyRequest(BaseAdminHandler):
    def get(self, *args, **kwargs):
        if not super(ApplyRequest, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        return_url = self.request.get('return_url')
        key = ndb.Key(urlsafe=url_key)
        request = key.get()
        group = Group(group_id=request.group_id,
                      name=request.name,
                      origin=request.origin,
                      admin=request.admin)
        group.put()
        key.delete()
        self.redirect(return_url)



##\brief Подать заявку на добавление группы
class RegisterGroup(BaseHandler):
    def get(self, *args, **kwargs):
        super(RegisterGroup, self).get(*args, **kwargs)
        template = JINJA_ENVIRONMENT.\
            get_template('templates/register_group.html')
        group = Group(group_id='group',
                      name='',
                      origin='',
                      admin=[])
        self.render_data['group'] = group
        self.response.write(template.render(self.render_data))

    def post(self, *args, **kwargs):
        super(RegisterGroup, self).get(*args, **kwargs)
        group_id = self.request.get('group_id')
        name = self.request.get('name')
        origin = self.request.get('origin')
        admin_raw = self.request.get('admin').lower()
        admin = re.split(';| |,|\*|\n',admin_raw)
        info = self.request.get('info')
        group = Premoderated_Group(group_id=group_id,
                                   name=name,
                                   origin=origin,
                                   admin=admin)
        group.put()
        message = mail.EmailMessage(sender="The Schedule Support <info@the-schedule.appspotmail.com>",
                                    to="Fedor Loktev <fmlokt@gmail.com>",
                                    cc="Nikolay Kalinin<nakalinin@gmail.com>",
                                    subject="You have new registration request",
                                    body="You have new registration request:\n" +\
                                    "Group id : " + group_id + " \n" +\
                                    "Name : " + name + " \n" +\
                                    "Origin : " + origin + " \n" +\
                                    "Admin : " + admin_raw + " \n" +\
                                    "Info : " + info + " \n" +\
                                    "---------\n" + "This message was generated automatically\n" +\
                                    "The Schedule.")
        message.send()
        self.response.write('Спасибо, заявка будет рассмотрена. Мы обязательно с вами свяжемся')


