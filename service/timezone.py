# -*- coding: utf-8 -*-

from datetime import *

def now():
    return datetime.now() + timedelta(hours=3)


def today():
    return now().date()
