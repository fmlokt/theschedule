# -*- coding: utf-8 -*-

from datetime import *

def now():
    return datetime.now() + timedelta(hours=3)


def today():
    return now().date()


def datefromstr(strdate):
    return datetime.strptime(strdate, "%Y-%m-%d").date()


def timefromstr(strtime):
    return datetime.strptime(strtime, "%H:%M").time()


def gettimediff(time1, time2):
    return datetime.combine(today(), time1) - datetime.combine(today(), time2)


def addtime(time, delta):
    return (datetime.combine(today(), time) + delta).time()

