#!/usr/bin/env python
from __future__ import print_function, unicode_literals
from datetime import datetime, timedelta, date, time
import pytz

from django.test import TestCase
from django.contrib.auth.models import User

from dateutil import rrule
from eventcalendar.models import Event, EventCategory, Schedule, Occurrence


class EventTest(TestCase):
    def setUp(self):
        self.category = EventCategory.objects.create(name="Test Category", slug="test-category")
        self.user = User.objects.create(username="test", email='test@test.com')

    def test_slug_setting(self):
        event1 = Event.objects.create(
            title="Test Case",
            category=self.category,
            submitter=self.user
        )
        event2 = Event.objects.create(
            title="Test Case",
            category=self.category,
            submitter=self.user,
        )
        self.assertNotEqual(event1.slug, event2.slug)

    def test_single_schedule_nonrecurring(self):
        event1 = Event.objects.create(
            title="Test Case",
            category=self.category,
            submitter=self.user
        )
        est = pytz.timezone('US/Eastern')
        schedule = Schedule.objects.create(
            event=event1,
            begins=est.localize(datetime(2015, 6, 1, 17, 0)),
            duration=1.5
        )
        self.assertEquals(len(schedule._dates), 1)
        self.assertEquals(schedule.occurrences.count(), 1)

    def test_single_schedule_recurring(self):
        event1 = Event.objects.create(
            title="Test Case",
            category=self.category,
            submitter=self.user
        )
        est = pytz.timezone('US/Eastern')
        schedule = Schedule.objects.create(
            event=event1,
            begins=est.localize(datetime(2015, 6, 1, 17, 0)),
            duration=1.5,
            rrule_str='FREQ=DAILY;COUNT=10'
        )
        self.assertEquals(len(schedule._dates), 10)
        self.assertEquals(schedule.occurrences.count(), 10)
