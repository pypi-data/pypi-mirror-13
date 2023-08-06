# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kstore', '0003_mailmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='recipient',
            field=models.ForeignKey(related_name='destinatario', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='sender',
            field=models.ForeignKey(related_name='enviante', to=settings.AUTH_USER_MODEL),
        ),
    ]
