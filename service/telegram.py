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

from service import timezone
from service.secret import *
from objects.group import *
from objects.pair import *


BASE_URL = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/'
NAME = 'thescheduleBot'

# ================================

class ChatSettings(ndb.Model):
    # key name: str(chat_id)
    group_id = ndb.StringProperty(indexed=False, default='')


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', data=urllib.urlencode({'url': url})))))


def reply(chat_id, msg):
    if msg:
        resp = urllib2.urlopen(BASE_URL + 'sendMessage', data=urllib.urlencode({
            'chat_id': str(chat_id),
            'text': msg.encode('utf-8'),
        })).read()
        #resp = 'ok'
        #logging.info('message sent: ' + msg)
    else:
        logging.error('no txt msg or specified')
        resp = None
    logging.info('send response:')
    logging.info(resp)


def proceed_start(chat_id, fr, text):
    reply(chat_id, u'Здравствуйте, ' + str(fr['first_name']) + ' ' + str(fr['last_name']))


def proceed_time(chat_id, fr, text):
    reply(chat_id, u'Текущее время - ' + str((timezone.now() + datetime.timedelta(hours=3)).strftime('%H:%M')))


def proceed_weather(chat_id, fr, text):
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
    reply(chat_id, u'Погода на ' + hour + u' час(а) ' + day  + u'.' + month  + u'.' + year + '\n' + u'От ' + min_temp + u' до ' + max_temp + u'градусов по Цельсию' +'\n' + u'Облачность ' + cloud + u'/3')


def proceed_help(chat_id, fr, text):
    text = u'Это бот проекта The Schedule.\nthe-schedule.appspot.com\n\nПоддерживаемые команды:\n'
    for command in COMMANDS:
        text += command[0] + '   -   ' + command[2] + '\n'
    reply(chat_id, text)


def proceed_set_groupid(chat_id, fr, text):
    text = text.strip()
    if text == '':
        reply(chat_id, u'Чтобы привязать чат к группе, наберите /set_group <id группы>.')
        return
    group = Group.query(Group.group_id == text).get()
    if group is None:
        reply(chat_id, u'Такой группы не существует!')
        return
    chat_settings = ChatSettings.get_or_insert(str(chat_id))
    chat_settings.group_id = text
    chat_settings.put()
    reply(chat_id, u'Id группы изменен на \"' + chat_settings.group_id + '\" (' + group.name + ', ' + group.origin + ').')


def proceed_groupid(chat_id, fr, text):
    chat_settings = ChatSettings.get_or_insert(str(chat_id))
    if chat_settings.group_id == '':
        reply(chat_id, u'Чат не привязан ни к какой группе. Чтобы привязать, наберите /set_group <id группы>.')
    else:
        group = Group.query(Group.group_id == chat_settings.group_id).get()
        reply(chat_id, u'Id группы: \"' + chat_settings.group_id + '\" (' + group.name + ', ' + group.origin + ').')


def proceed_next(chat_id, fr, text):
    chat_settings = ChatSettings.get_or_insert(str(chat_id))
    if chat_settings.group_id == '':
        reply(chat_id, u'Чат не привязан ни к какой группе. Чтобы привязать, наберите /set_group <id группы>.')
    else:
        event_list = ScheduledPair.query(ScheduledPair.group_id == chat_settings.group_id, ScheduledPair.date == timezone.today(), ScheduledPair.start_time > (timezone.now() - datetime.timedelta(minutes=10)).time()).order(ScheduledPair.start_time).fetch(3)
        if len(event_list) == 0:
            reply(chat_id, u'Сегодня больше нет событий.')
            return
        text = u'Ближайшие события сегодня:\n\n'
        for event in event_list:
            text += event.classname + u'\nНачало в ' + event.start_time.strftime('%H:%M') + '.\n\n'
        reply(chat_id, text)


COMMANDS = [
    ['/start', proceed_start, u'начать работу'],
    ['/time', proceed_time, u'текущее время'],
    ['/weather', proceed_weather, u'текущая погода'],
    ['/set_group', proceed_set_groupid, u'привязать чат к группе'],
    ['/group', proceed_groupid, u'показать группу, к которой привязан чат'],
    ['/next', proceed_next, u'показать следующее событие из расписания группы'],
    ['/help', proceed_help, u'показать данную справку']
]


def proceed_command(chat_id, fr, command, text):
    logging.info('recieved command: ' + command + ', text: ' + text);
    if (text.startswith('@') and not text.startswith('@' + NAME)):
        logging.info('This command is not for us')
        return
    if text.startswith('@'):
        if text.find(' ') != -1:
            text = text[text.find(' '):]
        else:
            text = ''
    for possible_command in COMMANDS:
        if possible_command[0] == command:
            possible_command[1](chat_id, fr, text)
            return
    reply(chat_id, u'Какая команда?')


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)

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


        if text.startswith('/'):
            command_end = len(text)
            if text.find(' ') != -1:
                command_end = min(command_end, text.find(' '))
            if text.find('@') != -1:
                command_end = min(command_end, text.find('@'))
            proceed_command(chat_id, fr, text[:command_end], text[command_end:])
        elif 'what time is it' in text:
            reply(chat_id, 'It is ASGAP time')
        else:
            reply(chat_id, u'Я не понимаю')


app = webapp2.WSGIApplication([
    ('/telegram/me', MeHandler),
    ('/telegram/updates', GetUpdatesHandler),
    ('/telegram/set_webhook', SetWebhookHandler),
    ('/telegram/webhook', WebhookHandler)
], debug=True)
