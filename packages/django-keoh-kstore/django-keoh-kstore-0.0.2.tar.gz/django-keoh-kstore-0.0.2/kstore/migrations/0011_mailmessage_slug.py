# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0010_mailmessage_sended_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='slug',
            field=models.SlugField(default='se'),
            preserve_default=False,
        ),
    ]
