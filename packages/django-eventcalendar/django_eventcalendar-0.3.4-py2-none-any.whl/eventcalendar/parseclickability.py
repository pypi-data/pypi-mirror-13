#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from dateutil.parser import parse
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from eventcalendar.models import Event, EventCategory, Schedule, Venue
import markdown2
import xml.etree.ElementTree as ET

user = User.objects.get(username='coordt')
Category = namedtuple('Category', ('id', 'setname', 'name', 'path'))
MediaRelation = namedtuple('MediaRelation', ('filename', 'height', 'width'))
media = {}  # keyed by id
placements = {}
eventtypes = dict((x.id, x) for x in EventCategory.objects.all())
mimetypes = {
    'jpg': 'image/jpeg',
    'JPG': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
}

categories = {
    '242179': eventtypes[2],
    '242259': eventtypes[20],
    '242219': eventtypes[9],
    '242264': eventtypes[21],
    '242229': eventtypes[11],
    '242224': eventtypes[10],
    '261757': eventtypes[12],
    '242184': eventtypes[3],
    '242234': eventtypes[14],
    '242239': eventtypes[15],
    '242189': eventtypes[4],
    '261762': eventtypes[16],
    '242194': eventtypes[5],
    '242269': eventtypes[22],
    '242274': eventtypes[23],
    '242244': eventtypes[17],
    '242249': eventtypes[18],
    '242199': eventtypes[32],
    '242254': eventtypes[19],
    '242214': eventtypes[8],
    '242204': eventtypes[6],
    '242279': eventtypes[24],
    '242209': eventtypes[7],
    '242294': eventtypes[28],
    '242174': eventtypes[1],
    '242314': eventtypes[30],
    '955933': eventtypes[31],
    '242284': eventtypes[25],
    '242289': eventtypes[26],
}


def make_event(record):
    """
    Convert a record into an event
    """
    try:
        Event.objects.get(external_id=record['id'])
        print "skipping", record['id']
        return
    except Event.DoesNotExist:
        pass
    if record['isTwentyOne'] == 'true':
        min_age = 21
    else:
        min_age = 0

    if record['media_relations']:
        img = record['media_relations'][0].filename
        img_height = record['media_relations'][0].height
        img_width = record['media_relations'][0].width
    else:
        img = img_height = img_width = None
    print "creating", record['id']
    e = Event.objects.create(
        title=record['title'],
        more_info_phone=record['phone'][:50],
        description=record['body'] or '',
        more_info_url=record['eventURL'][:200],
        min_age=min_age,
        max_age=100,
        image=img,
        image_height=img_height,
        image_width=img_width,
        raw_location=force_str("{locationText}, {addressText}, {cityText} {stateText}".format(**record)),
        category=record['categories'][0],
        submitter=user,
        external_id=record['id'][:50],
        approved=True,
    )
    if e.parsable_address and e.parsed_address['name']:
        v = Venue.objects.filter(name=e.parsed_address['name'])
        if len(v) == 1:
            e.venue = v[0]
            e.neighborhood = e.venue.neighborhood
        else:
            e.location_name = e.parsed_address['name']
        e.save()

    for i in record['schedules']:
        Schedule.objects.create(
            event=e,
            begins=i['start'],
            duration=i['duration'],
            rrule_str=i['rrule'],
        )


def make_placement(wp_element):
    """
    Convert a websitePlacement element into the placement name
    """
    name = wp_element.find('section').text.lower()

    if name not in placements:
        placements[name] = name

    return placements[name]


def make_category(element):
    """
    Convert a categorySet tag into a Category
    """
    cat_el = element.find('category')
    cat_id = cat_el.attrib['id']
    if cat_id in categories:
        return categories[cat_id]

    set_name = element.find('setName').text
    cat_name = cat_el.find('name').text
    cat_path = cat_el.find('path').text
    if set_name == 'Event Type':
        print "Missing", cat_name, cat_id
        categories[cat_id] = Category(id=cat_id, setname=set_name, name=cat_name, path=cat_path)
    else:
        return None
    return cat_id


def make_mediarelation(mp_element):
    """
    Convert a mediaPlacement element into a dict
    """
    mediatag = mp_element.find('media')
    relation = MediaRelation(
        filename=mediatag.find('filename').text,
        height=getattr(mediatag.find('height'), 'text', 0),
        width=getattr(mediatag.find('width'), 'text', 0),
    )
    return relation


def make_schedule(schedule):
    """
    Parse a schedule element to make a start date and time and duration
    """
    import datetime
    end_date = getattr(schedule.find('endDate'), 'text', '')
    end_time = getattr(schedule.find('endTime'), 'text', '17:00:00')
    start_date = getattr(schedule.find('startDate'), 'text', '')
    start_time = getattr(schedule.find('startTime'), 'text', '08:00:00')
    if start_date == '':
        raise Exception("Missing a start date")
    if end_date == '':
        raise Exception("Missing an end date")
    start_date = parse(start_date, tzinfos={'EST': -18000})
    end_date = parse(end_date, tzinfos={'EST': -18000})
    start_time = datetime.datetime.strptime(start_time, '%H:%M:%S')
    end_time = datetime.datetime.strptime(end_time, '%H:%M:%S')

    start = start_date.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
    end = end_date.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)

    if end.hour < start.hour:
        duration = float((24 - start.hour) + end.hour)
    else:
        duration = float(end.hour - start.hour)

    duration += (end.minute - start.minute) / 60.0
    rrule = ""

    if end.date() != start.date():
        end_plus_one = end + datetime.timedelta(days=1)
        rrule = "EVERY DAY UNTIL %s" % end_plus_one.strftime("%Y-%m-%d")

    return {'start': start, 'duration': duration, 'rrule': rrule}


def make_record(content):

    rec = {
        'id': content.attrib['id'],
        'content_type': content.find('contentType').text,
        'media_relations': [],
        'categories': [],
        'placements': [],
        'schedules': [],
        'locationText': '',
        'body': '',
        'create_date': parse(content.find('createDate').text, tzinfos={'EST': -18000}),
        'modified_date': parse(content.find('modifiedDate').text, tzinfos={'EST': -18000}),
        'status': content.find('status').text,
    }
    for field in content.findall('field'):
        if field.text:
            if field.attrib['name'] == 'body':
                rec[field.attrib['name']] = markdown2.markdown(force_str(field.text.strip()))
            else:
                rec[field.attrib['name']] = force_str(field.text.strip())
        else:
            rec[field.attrib['name']] = u''

    media_array = content.find('mediaPlacementsArray')
    for mpElement in media_array.findall('mediaPlacement'):
        rec['media_relations'].append(make_mediarelation(mpElement))

    for cat in content.find('categorization').findall('categorySet'):
        c = make_category(cat)
        if c is not None:
            rec['categories'].append(c)

    placement_urls = content.find('websitePlacementURLs')
    if placement_urls is not None:
        for web_placement in placement_urls.findall('websitePlacement'):
            rec['placements'].append(make_placement(web_placement))
    schedule = content.find('schedule')
    rec['schedules'].append(make_schedule(schedule))
    return rec


def importfile(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    records = []
    for content in root.iter('content'):
        record = make_record(content)
        records.append(record)
        make_event(record)
    return records


def clean():
    from eventcalendar.models import Occurrence
    Schedule.objects.all().delete()
    Occurrence.objects.all().delete()
    Event.objects.all().delete()


def run(filepath):
    return importfile(filepath)
