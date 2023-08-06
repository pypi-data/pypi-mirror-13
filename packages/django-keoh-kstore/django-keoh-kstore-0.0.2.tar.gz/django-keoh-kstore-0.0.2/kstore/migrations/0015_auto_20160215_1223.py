# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('kstore', '0014_mailmessage_important'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailmessage',
            name='message',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
    ]
