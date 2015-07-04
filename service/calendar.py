# -*- coding: utf-8 -*-

import os
import httplib2
from oauth2client import *
from apiclient import *
from environment import JINJA_ENVIRONMENT
from google.appengine.ext import webapp
from oauth2client.appengine import AppAssertionCredentials
from httplib2 import Http
from apiclient import discovery
from apiclient.discovery import build
from handlers.basehandler import *

##\brief Календарь
def CreateEvent_func(calendar_id, summary, start_time, end_time, description):
    credentials = AppAssertionCredentials(
        'https://www.googleapis.com/auth/calendar')
    http_auth = credentials.authorize(Http())
    calendar = build('calendar', 'v3', http=http_auth)
    service = discovery.build('calendar', 'v3', http=http_auth) #это часть для auth, нужна везде
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time + ':00+03:00' #html возвращает в формате немного другом
        },
        'end': {
            'dateTime': end_time + ':00+03:00'
        },
        'description': description
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return event['id']

def DeleteEvent_func(calendarId, eventId):
    credentials = AppAssertionCredentials(
        'https://www.googleapis.com/auth/calendar')
    http_auth = credentials.authorize(Http())
    calendar = build('calendar', 'v3', http=http_auth)
    service = discovery.build('calendar', 'v3', http=http_auth)

    service.events().delete(calendarId=calendarId, eventId=eventId).execute()

def CreateCalendar(group):
    credentials = AppAssertionCredentials(
        'https://www.googleapis.com/auth/calendar')
    http_auth = credentials.authorize(Http())
    calendar = build('calendar', 'v3', http=http_auth)
    service = discovery.build('calendar', 'v3', http=http_auth)

    calendar = {
        'summary': group,
        'timeZone': 'Europe/Moscow'
    }

    rule = {
        'scope': {
            'type': 'default' #это настройки календаря, например сделать публичным для подписки
            },
        'role': 'reader'
        }

    created_calendar = service.calendars().insert(body=calendar).execute()
    created_rule = service.acl().insert(calendarId='primary', body=rule).execute()
    return created_calendar['id']

def EventList(calendarId):
    events = service.events().list(calendarId=calendarId).execute()
    for event in events['items']:
         event_list = str(event['id']) + '\n'
    return event_list

def DeleteCalendar(calendarId):
    service.calendars().delete(calendarId).execute()


class CreateEvent(BaseAdminHandler):
    def get(self):
        if not super(CreateEvent, self).get():
            return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/calendar.html')
        self.response.write(template.render())

    def post(self):
        summary = self.request.get('summary')
        start = self.request.get('start')
        end = self.request.get('end')
        desc = self.request.get('desc')
        calendar = self.request.get('cal')
        event = CreateEvent_func(calendar, summary, start, end, desc)
        self.response.write('Event Id: ' + str(event))


class CalendarStatus(BaseAdminHandler):
    def get(self):
        if not super(CalendarStatus, self).get():
            return
        credentials = AppAssertionCredentials(
            'https://www.googleapis.com/auth/calendar')
        http_auth = credentials.authorize(Http())
        calendar = build('calendar', 'v3', http=http_auth)
        service = discovery.build('calendar', 'v3', http=http_auth)

        template = JINJA_ENVIRONMENT.\
            get_template('templates/calendar_status.html')
        calendars = service.calendarList().list().execute()
        self.render_data['calendars'] = []
        item = {}
        for calendar in calendars['items']:
            self.render_data['calendars'].append(calendar)
        self.response.write(template.render(self.render_data))

class DeleteEvent(BaseAdminHandler):
    def post(self):
        calendar = self.request.get('calendar')
        event = self.request.get('event')
        delete = DeleteEvent_func(calendar, event)
        self.response.write('Event Deleted: ' + str(event))








