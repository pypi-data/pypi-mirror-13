# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parse_push', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
