# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0013_auto_20160215_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='important',
            field=models.BooleanField(default=False),
        ),
    ]
