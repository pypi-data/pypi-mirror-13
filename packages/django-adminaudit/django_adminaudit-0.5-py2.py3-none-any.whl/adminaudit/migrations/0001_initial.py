# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.TextField()),
                ('user_id', models.IntegerField()),
                ('model', models.TextField()),
                ('change', models.CharField(max_length=100)),
                ('representation', models.TextField()),
                ('values', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
            ],
        ),
    ]
