# -*- coding: utf-8 -*-

import os

import jinja2

from handlers.localization import *


def format_time(value):
    return value.strftime('%H:%M')

def format_weekday(value):
    if type(value) is int:
        return russian_week(value % 7)
    else:
        return russian_week(value.weekday())

def format_date(value):
    return value.strftime('%d') + ' ' + russian_month(value.month)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape']
)

JINJA_ENVIRONMENT.filters['time'] = format_time
JINJA_ENVIRONMENT.filters['weekday'] = format_weekday
JINJA_ENVIRONMENT.filters['date'] = format_date
