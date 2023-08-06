# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0005_mailmessage_readed'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
