# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import enumerify.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(unique=True, max_length=100)),
                ('kind', enumerify.fields.SelectIntegerField(default=0, db_index=True, choices=[(0, b'iOS'), (1, b'Android'), (2, b'Windows RT'), (3, b'Windows Phone'), (4, b'.NET')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('token', 'kind')]),
        ),
    ]
