# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-08-14 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_job_chain'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='erro',
            field=models.BooleanField(default=False),
        ),
    ]
