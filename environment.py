# -*- coding: utf-8 -*-

import os

import jinja2


def format_time(value):
    return value.strftime('%H:%M')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape']
)

JINJA_ENVIRONMENT.filters['time'] = format_time
