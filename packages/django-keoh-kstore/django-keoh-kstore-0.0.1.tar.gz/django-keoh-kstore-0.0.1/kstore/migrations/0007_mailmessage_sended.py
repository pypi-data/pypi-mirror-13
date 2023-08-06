# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0006_mailmessage_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='sended',
            field=models.BooleanField(default=False),
        ),
    ]
