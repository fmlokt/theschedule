# -*- coding: utf-8 -*-

from environment import JINJA_ENVIRONMENT
from objects.subject import Subject
from handlers.basehandler import *


class ShowSubject(BaseHandler):
    def get(self, *args, **kwargs):
        super(ShowSubject, self).get(*args, **kwargs)
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        subject = key.get()
        template = JINJA_ENVIRONMENT.get_template('templates/show_subject.html')
        self.render_data['subject'] = subject
        self.response.write(template.render(self.render_data))


class NewSubject(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(NewSubject, self).get(*args, **kwargs):
            return
        subject = Subject(classname='',
                          teacher='')
        template = JINJA_ENVIRONMENT.get_template('templates/edit_subject.html')
        self.render_data['subject'] = subject
        self.response.write(template.render(self.render_data))


class EditSubject(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(EditSubject, self).get(*args, **kwargs):
            return
        url_key = self.request.get('key')
        key = ndb.Key(urlsafe=url_key)
        subject = key.get()
        template = JINJA_ENVIRONMENT.get_template('templates/edit_subject.html')
        self.render_data['subject'] = subject
        self.render_data['key_urlsafe'] = url_key
        self.response.write(template.render(self.render_data))


##\brief Список предметов
class ShowSubjects(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        group_id = kwargs.get('group_id')
        if not super(ShowSubjects, self).get(*args, **kwargs):
            return
        subjects_qry = Subject.query(Subject.group_id ==
                                     group_id)
        template = JINJA_ENVIRONMENT.get_template('templates/subjects.html')
        self.render_data['subjects'] = []
        for subject in subjects_qry:
            subject.edit_link = '/' + group_id + '/edit_subject?key=' +\
                             subject.key.urlsafe()
            subject.delete_link = '/' + group_id + '/delete_subject?key=' +\
                subject.key.urlsafe() + '&return_url=/' + group_id + '/subjects'
            self.render_data['subjects'].append(subject)
        self.response.write(template.render(self.render_data))

    def post(self, *args, **kwargs):
        if not super(ShowSubjects, self).post(*args, **kwargs):
            return
        classname = self.request.get('classname')
        teacher = self.request.get('teacher')
        url_key = self.request.get('key')
        group_id = kwargs.get('group_id')
        if url_key != '':
            key = ndb.Key(urlsafe=url_key)
            subject = key.get()
            subject.classname = classname
            subject.teacher = teacher
            subject.group_id = group_id
        else:
            subject = Subject(classname=classname,
                              teacher=teacher,
                              group_id=group_id)
        subject.put()
        self.redirect('/' + group_id + '/subjects')


##\brief Удалить предмет
class DeleteSubject(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        if not super(DeleteSubject, self).post(*args, **kwargs):
            return
        url_key = self.request.get('key')
        return_url = self.request.get('return_url')
        key = ndb.Key(urlsafe=url_key)
        key.delete()
        self.redirect(return_url)
