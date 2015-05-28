# -*- coding: utf-8 -*-

import oauth2client
from oauth2client.client import SignedJwtAssertionCredentials
from httplib2 import Http
from apiclient.discovery import build

##\brief Добавить событие в календарь
def add_cal_record():
    client_email = '261993259110-1m85s0ct6iosj9571ck2682h7irivquu@developer.gserviceaccount.com'
    with open("TheSchedule-9bd45c6dec1c.p12") as f:
        private_key = f.read()

    credentials = SignedJwtAssertionCredentials(client_email, private_key,
        'https://www.googleapis.com/auth/sqlservice.admin')
    http_auth = credentials.authorize(Http())
    calendar = build('calendar', 'v3', http=http_auth)
    event = {
        'summary': 'Appointment',
        'start': {
            'dateTime': '2015-05-25T10:00:00.000+03:00'
        },
        'end': {
            'dateTime': '2015-05-25T10:25:00.000+03:00'
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print created_event

##\brief Календарь
class Calendar(BaseLocalAdminHandler):
    def get(self):
        add_cal_record()

