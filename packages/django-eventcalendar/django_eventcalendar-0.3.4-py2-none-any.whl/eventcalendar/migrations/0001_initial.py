# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import eventcalendar.fields
import django.contrib.gis.db.models.fields
import django.utils.timezone
import django.core.files.storage
from django.conf import settings
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='name of event')),
                ('slug', eventcalendar.fields.AutoSlugField(populate_from=b'title', verbose_name='slug', max_length=255, editable=False, blank=True)),
                ('description', models.TextField(default=b'', verbose_name='description', blank=True)),
                ('location_name', models.CharField(max_length=255, null=True, verbose_name='location name', blank=True)),
                ('raw_location', models.CharField(max_length=255, null=True, verbose_name='location address', blank=True)),
                ('latlong', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name='latitude-longitude', blank=True)),
                ('min_age', models.PositiveIntegerField(default=0, null=True, verbose_name='minimum age', blank=True)),
                ('max_age', models.PositiveIntegerField(default=100, null=True, verbose_name='maximum age', blank=True)),
                ('more_info_url', models.URLField(null=True, verbose_name='URL for more info', blank=True)),
                ('more_info_phone', models.CharField(max_length=50, null=True, verbose_name='Phone for more info', blank=True)),
                ('tickets_url', models.URLField(null=True, verbose_name='URL for tickets', blank=True)),
                ('image', models.FileField(upload_to=b'', null=True, verbose_name='event image', blank=True)),
                ('image_width', models.PositiveIntegerField(null=True, verbose_name='image width', blank=True)),
                ('image_height', models.PositiveIntegerField(null=True, verbose_name='image height', blank=True)),
                ('price_info', django_hstore.fields.DictionaryField(null=True, verbose_name='price info', blank=True)),
                ('origin', models.CharField(help_text=b'The source domain for that originated this event submission', max_length=255, null=True, verbose_name='origin', blank=True)),
                ('approved', models.BooleanField(default=False, verbose_name='approved')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('event_type', models.CharField(default=b'Event', help_text=b'Used in microformats to better indicate the type of event.', max_length=50, verbose_name='event type', choices=[(b'BusinessEvent', b'Business Event'), (b'ChildrensEvent', b'Childrens Event'), (b'ComedyEvent', b'Comedy Event'), (b'DanceEvent', b'Dance Event'), (b'DeliveryEvent', b'Delivery Event'), (b'EducationEvent', b'Education Event'), (b'Festival', b'Festival'), (b'FoodEvent', b'Food Event'), (b'Event', b'Generic Event'), (b'LiteraryEvent', b'Literary Event'), (b'MusicEvent', b'Music Event'), (b'PublicationEvent', b'Publication Event'), (b'SaleEvent', b'Sale Event'), (b'ScreeningEvent', b'Screening Event'), (b'SocialEvent', b'Social Event'), (b'SportsEvent', b'Sports Event'), (b'TheaterEvent', b'Theater Event'), (b'VisualArtsEvent', b'Visual Arts Event')])),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'event type',
                'verbose_name_plural': 'event types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Neighborhood',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', eventcalendar.fields.AutoSlugField(populate_from=b'name', verbose_name='slug', max_length=255, editable=False, blank=True)),
                ('geography', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'neighborhood',
                'verbose_name_plural': 'neighborhoods',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField(verbose_name='start time')),
                ('end_time', models.DateTimeField(verbose_name='end time')),
                ('event', models.ForeignKey(related_name='occurrences', editable=False, to='eventcalendar.Event', verbose_name='event')),
            ],
            options={
                'ordering': ('start_time', 'end_time'),
                'verbose_name': 'occurrence',
                'verbose_name_plural': 'occurrences',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('begins', models.DateTimeField(default=django.utils.timezone.now, verbose_name='begins')),
                ('duration', models.DecimalField(default=1.0, verbose_name='duration', max_digits=4, decimal_places=2)),
                ('schedule_text', models.TextField(null=True, verbose_name='schedule text', blank=True)),
                ('rrule_str', models.TextField(null=True, verbose_name='recurring rule', blank=True)),
                ('event', models.ForeignKey(related_name='schedules', verbose_name='event', to='eventcalendar.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', models.SlugField(max_length=255, verbose_name='slug')),
                ('address', models.CharField(max_length=255, verbose_name='address')),
                ('phone', models.CharField(max_length=25, null=True, verbose_name='phone', blank=True)),
                ('website', models.URLField(max_length=255, null=True, verbose_name='web site', blank=True)),
                ('latlong', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name='latitude-longitude', blank=True)),
                ('image', models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'', null=True, verbose_name='image', blank=True)),
                ('special_instructions', models.TextField(null=True, verbose_name='special instructions', blank=True)),
                ('neighborhood', models.ForeignKey(verbose_name='neighborhood', blank=True, to='eventcalendar.Neighborhood', null=True)),
            ],
            options={
                'verbose_name': 'Venue',
                'verbose_name_plural': 'Venues',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VenueCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('slug', models.SlugField(verbose_name='slug')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'venue type',
                'verbose_name_plural': 'venue types',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='venue',
            name='venue_type',
            field=models.ForeignKey(verbose_name='venue type', blank=True, to='eventcalendar.VenueCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='occurrence',
            name='schedule',
            field=models.ForeignKey(related_name='occurrences', editable=False, to='eventcalendar.Schedule', verbose_name='schedule'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(verbose_name='category', to='eventcalendar.EventCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='neighborhood',
            field=models.ForeignKey(verbose_name='neighborhood', blank=True, to='eventcalendar.Neighborhood', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='submitter',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='venue',
            field=models.ForeignKey(verbose_name='venue', blank=True, to='eventcalendar.Venue', null=True),
            preserve_default=True,
        ),
    ]
