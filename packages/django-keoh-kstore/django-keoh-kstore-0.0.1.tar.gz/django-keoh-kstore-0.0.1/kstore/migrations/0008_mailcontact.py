# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kstore', '0007_mailmessage_sended'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(related_name='Contacto', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
