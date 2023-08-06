# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0015_auto_20160215_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='uuid',
            field=uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
