# -*- coding: utf-8 -*-


def russian_week(n):
    russian_week = [u'Понедельник', u'Вторник', u'Среда',
                    u'Четверг', u'Пятница', u'Суббота']
    return russian_week[n]


def russian_month(n):
    russian_month = [u'Января', u'Февраля', u'Марта',
                     u'Апреля', u'Мая', u'Июня',
                     u'Июля', u'Августа', u'Сентября',
                     u'Октября', u'Ноября', u'Декабря']
    return russian_month[n-1]
