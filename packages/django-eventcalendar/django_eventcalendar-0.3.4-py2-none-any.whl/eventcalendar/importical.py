#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_import_user():
    from .settings import IMPORT_USERNAME, DEFAULT_ORIGIN
    from django.contrib.auth.models import User
    try:
        return User.objects.get(username=IMPORT_USERNAME)
    except User.DoesNotExist:
        return User.objects.create(
            username=IMPORT_USERNAME,
            email="%s@%s" % (IMPORT_USERNAME, DEFAULT_ORIGIN)
        )


def import_icalfile(filepath, category_slug):
    from icalendar import Calendar
    from eventcalendar.models import Event, EventCategory
    import HTMLParser

    cal = Calendar.from_ical(open(filepath, 'rb').read())
    user = get_import_user()
    eventcategory = EventCategory.objects.get(slug=category_slug)
    h = HTMLParser.HTMLParser()

    for event in cal.walk('vevent'):
        e = Event.objects.create(
            title=h.unescape(unicode(event['SUMMARY'])),
            description=h.unescape(unicode(event.get('DESCRIPTION', ''))),
            min_age=0,
            max_age=100,
            more_info_url=unicode(event.get('URL', '')),
            raw_location=h.unescape(unicode(event.get('LOCATION', ''))),
            category=eventcategory,
            submitter=user,
            origin="example.com",
            approved=True,
        )
        if 'DTEND' in event:
            duration = event['DTEND'].dt - event['DTSTART'].dt
            duration = duration.total_seconds() / 60 / 60
        else:
            duration = 1
        e.schedules.create(
            begins=event['DTSTART'].dt,
            duration=duration
        )
