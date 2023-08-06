# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0011_mailmessage_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='basicconfiguration',
            name='theme',
            field=models.CharField(default=b'one', max_length=255, verbose_name=b'Theme'),
        ),
    ]
