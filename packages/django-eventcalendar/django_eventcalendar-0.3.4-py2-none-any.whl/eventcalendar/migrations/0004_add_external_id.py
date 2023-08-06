# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('eventcalendar', '0003_add_descriptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='external_id',
            field=models.CharField(max_length=50, null=True, verbose_name='external ID', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.FileField(max_length=255, upload_to=b'', null=True, verbose_name='event image', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='venue',
            name='image',
            field=models.FileField(upload_to=b'', storage=django.core.files.storage.FileSystemStorage(), max_length=255, blank=True, null=True, verbose_name='image'),
            preserve_default=True,
        ),
    ]
