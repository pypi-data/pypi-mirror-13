# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kstore', '0008_mailcontact'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailcontact',
            name='owner',
            field=models.ForeignKey(related_name='registrador_de_contacto', default=0, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
