# -*- coding: utf-8 -*-

import os
import calendar
import datetime

import webapp2
from google.appengine.api import memcache

from service import timezone
from objects.schedule import *
from environment import JINJA_ENVIRONMENT
from objects.pair import *
from handlers.basehandler import *
from service.telegram import *

##\brief Удаляет старые пары
class DeleteOld(BaseHandler):
    def get(self):
        pairs_qry = ScheduledPair.query(ScheduledPair.date <
                                        timezone.today())
        for pair in pairs_qry:
            pair.key.delete()


class SendChanges(BaseHandler):
    def get(self):
        groups = Group.query()
        for group in groups:
            pairs_qry = ScheduledPair.query(ScheduledPair.group_id == group.group_id,
                                            ScheduledPair.date == timezone.today() + datetime.timedelta(days=1),
                                            ScheduledPair.replace == True).order(ScheduledPair.start_time)
            text = u''
            for pair in pairs_qry:
                if pair.pair_type == 'cancel':
                    text += u'❌' + u'Занятие ОТМЕНЕНО:\n'
                else:
                    text += u'🔀' + u'Изменение:\n'
                text += pair.classname + u'\nНачало в ' + pair.start_time.strftime('%H:%M') + '.'
                text += '\n\n'
            logging.info(text)
            if text == u'':
                continue
            text = u'ℹ' + u' Внимание! На завтра имеются изменения в расписании!\n\n' + text + u'Полное расписание на завтра: /tomorrow.'
            chats = ChatSettings.query(ChatSettings.group_id == group.group_id)
            for chat in chats:
                #logging.info("send changes to " + str(chat.key.id()))
                reply(chat.key.id(), text)

