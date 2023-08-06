# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0012_basicconfiguration_theme'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 15, 9, 28, 18, 635423, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='sended_at',
            field=models.DateTimeField(blank=True),
        ),
    ]
