# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0009_mailcontact_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='sended_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 1, 18, 14, 38, 579222, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
