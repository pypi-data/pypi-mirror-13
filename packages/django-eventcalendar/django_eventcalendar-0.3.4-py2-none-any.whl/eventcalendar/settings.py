# -*- coding: utf-8 -*-
from django.conf import settings as site_settings
from django.core.files.storage import get_storage_class
from django.utils.translation import ugettext_lazy as _
import datetime
from dateutil import rrule

DEFAULT_SETTINGS = {
    'STORAGE': None,
    # A "strftime" string for formatting start and end time selectors in forms
    "TIMESLOT_TIME_FORMAT": '%I:%M %p',

    # Used for creating start and end time form selectors as well as time slot grids.
    # Value should be datetime.timedelta value representing the incremental
    # differences between temporal options
    "TIMESLOT_INTERVAL": datetime.timedelta(minutes=15),

    # A datetime.time value indicting the starting time for time slot grids and
    # form selectors
    "TIMESLOT_START_TIME": datetime.time(9),

    # A datetime.timedelta value indicating the offset value from
    # TIMESLOT_START_TIME for creating time slot grids and form selectors. The for
    # using a time delta is that it possible to span dates. For instance, one could
    # have a starting time of 3pm (15:00) and wish to indicate a ending value
    # 1:30am (01:30), in which case a value of datetime.timedelta(hours=10.5)
    # could be specified to indicate that the 1:30 represents the following date's
    # time and not the current date.
    "TIMESLOT_END_TIME_DURATION": datetime.timedelta(hours=+8),

    # Indicates a minimum value for the number grid columns to be shown in the time
    # slot table.
    "TIMESLOT_MIN_COLUMNS": 4,

    # Indicate the default length in time for a new occurrence, specifed by using
    # a datetime.timedelta object
    "DEFAULT_OCCURRENCE_DURATION": datetime.timedelta(hours=+1),

    # If not None, passed to the calendar module's setfirstweekday function.
    "CALENDAR_FIRST_WEEKDAY": 6,
    "WEEKDAY_SHORT": (
        (7, _('Sun')),
        (1, _('Mon')),
        (2, _('Tue')),
        (3, _('Wed')),
        (4, _('Thu')),
        (5, _('Fri')),
        (6, _('Sat'))
    ),
    "WEEKDAY_LONG": (
        (7, _('Sunday')),
        (1, _('Monday')),
        (2, _('Tuesday')),
        (3, _('Wednesday')),
        (4, _('Thursday')),
        (5, _('Friday')),
        (6, _('Saturday'))
    ),
    "MONTH_LONG": (
        (1, _('January')),
        (2, _('February')),
        (3, _('March')),
        (4, _('April')),
        (5, _('May')),
        (6, _('June')),
        (7, _('July')),
        (8, _('August')),
        (9, _('September')),
        (10, _('October')),
        (11, _('November')),
        (12, _('December')),
    ),
    "MONTH_SHORT": (
        (1, _('Jan')),
        (2, _('Feb')),
        (3, _('Mar')),
        (4, _('Apr')),
        (5, _('May')),
        (6, _('Jun')),
        (7, _('Jul')),
        (8, _('Aug')),
        (9, _('Sep')),
        (10, _('Oct')),
        (11, _('Nov')),
        (12, _('Dec')),
    ),
    "ORDINAL": (
        (1, _('first')),
        (2, _('second')),
        (3, _('third')),
        (4, _('fourth')),
        (-1, _('last'))
    ),
    "FREQUENCY_CHOICES": (
        (rrule.DAILY, _('Day(s)')),
        (rrule.WEEKLY, _('Week(s)')),
        (rrule.MONTHLY, _('Month(s)')),
        (rrule.YEARLY, _('Year(s)')),
    ),
    "REPEAT_CHOICES": (
        ('count', _('By count')),
        ('until', _('Until date')),
    ),
    "ISO_WEEKDAYS_MAP": (
        None,
        rrule.MO,
        rrule.TU,
        rrule.WE,
        rrule.TH,
        rrule.FR,
        rrule.SA,
        rrule.SU
    ),
    'CATEGORY_TYPE_CHOICES': (
        ('BusinessEvent', 'Business Event'),
        ('ChildrensEvent', 'Childrens Event'),
        ('ComedyEvent', 'Comedy Event'),
        ('DanceEvent', 'Dance Event'),
        ('DeliveryEvent', 'Delivery Event'),
        ('EducationEvent', 'Education Event'),
        ('Festival', 'Festival'),
        ('FoodEvent', 'Food Event'),
        ('Event', 'Generic Event'),
        ('LiteraryEvent', 'Literary Event'),
        ('MusicEvent', 'Music Event'),
        ('PublicationEvent', 'Publication Event'),
        ('SaleEvent', 'Sale Event'),
        ('ScreeningEvent', 'Screening Event'),
        ('SocialEvent', 'Social Event'),
        ('SportsEvent', 'Sports Event'),
        ('TheaterEvent', 'Theater Event'),
        ('VisualArtsEvent', 'Visual Arts Event'),
    ),
    'DEFAULT_ORIGIN': 'example.com',
    'IMPORT_USERNAME': 'importuser',
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(site_settings, 'EVENTCALENDAR_SETTINGS', {}))
STORAGE_CLASS = get_storage_class(USER_SETTINGS['STORAGE'])

globals().update(USER_SETTINGS)
