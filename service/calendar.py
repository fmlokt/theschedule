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
def CreateEvent(calendarId ,summary, start_time, end_time, description):
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
    event = service.events().insert(calendarId=calendarId, body=event).execute()
    return event['id']

def DeleteEvent(calendarId, eventId):
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

def DeleteCalendar(calendarId):
    service.calendars().delete(calendarId).execute()


class Calendar(BaseAdminHandler):
    def get(self):
        if not super(Calendar, self).get():
            return
        template = JINJA_ENVIRONMENT.\
            get_template('templates/calendar.html')
        self.response.write(template.render())

    def post(self):
        summary = self.request.get('summary')
        start = self.request.get('start')
        end = self.request.get('end')
        desc = self.request.get('desc')
        event = CreateEvent('4eff584ar3hrm3cbe014aup5qo@group.calendar.google.com', summary, start, end, desc)
        self.response.write('Event Id: ' + str(event))




