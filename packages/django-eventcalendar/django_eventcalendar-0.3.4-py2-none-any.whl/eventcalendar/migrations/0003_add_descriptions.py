# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('eventcalendar', '0002_add_venue_img_dims'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='description',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=ckeditor.fields.RichTextField(default=b'', verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='venue',
            name='special_instructions',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='special instructions', blank=True),
            preserve_default=True,
        ),
    ]
