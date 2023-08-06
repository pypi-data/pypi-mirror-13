# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventcalendar', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='venue',
            options={'ordering': ('name',), 'verbose_name': 'Venue', 'verbose_name_plural': 'Venues'},
        ),
        migrations.AddField(
            model_name='venue',
            name='image_height',
            field=models.PositiveIntegerField(null=True, verbose_name='image height', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='venue',
            name='image_width',
            field=models.PositiveIntegerField(null=True, verbose_name='image width', blank=True),
            preserve_default=True,
        ),
    ]
