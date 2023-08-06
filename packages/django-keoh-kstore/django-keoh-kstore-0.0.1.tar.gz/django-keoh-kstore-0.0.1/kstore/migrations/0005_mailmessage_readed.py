# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0004_auto_20151218_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='readed',
            field=models.BooleanField(default=False),
        ),
    ]
