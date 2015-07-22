# -*- coding: utf-8 -*-

import StringIO
import json
import logging
import random
import urllib
import urllib2
import datetime

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

from handlers.basehandler import *
import xml.etree.ElementTree as ET


token = 'AUTH_TOKEN'
base_url = 'https://api.telegram.org/bot' + token + '/'

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ===============================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(base_url + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(base_url + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(base_url + 'setWebhook', data=urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg):
            if msg:
                resp = urllib2.urlopen(base_url + 'sendMessage', data=urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                })).read()
            else:
                logging.error('no txt msg or specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply(u'Здравствуйте, ' + str(fr['first_name']) + ' ' + str(fr['last_name']))
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply(u'Бот отключен')
                setEnabled(chat_id, False)
            elif text == '/time':
                reply(u'Текущее время - ' + str((datetime.datetime.now() + datetime.timedelta(hours=3)).strftime('%H:%M')))
            elif text == '/weather':
                link = 'http://xml.meteoservice.ru/export/gismeteo/point/120.xml'
                weather = urllib2.urlopen(link)
                tree = ET.parse(weather)
                root = tree.getroot()
                hour = root[0][0][0].attrib['hour']
                day =  root[0][0][0].attrib['day']
                month =  root[0][0][0].attrib['month']
                year =  root[0][0][0].attrib['year']
                max_temp = root[0][0][0][2].attrib['max']
                min_temp = root[0][0][0][2].attrib['min']
                cloud = root[0][0][0][0].attrib['cloudiness']
                reply(u'Погода на ' + hour + u' час(а) ' + day  + u'.' + month  + u'.' + year + '\n' + u'От ' + min_temp + u' до ' + max_temp + u'градусов по Цельсию' +'\n' + u'Облачность ' + cloud + u'/3')
            else:
                reply(u'Какая команда?')

        elif 'what time is it' in text:
            reply('It is ASGAP time')
        else:
            reply(u'Я не понимаю')


app = webapp2.WSGIApplication([
    ('/telegram/me', MeHandler),
    ('/telegram/updates', GetUpdatesHandler),
    ('/telegram/set_webhook', SetWebhookHandler),
    ('/telegram/webhook', WebhookHandler)
], debug=True)