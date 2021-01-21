# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2021-01-21 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_job_tksamc_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='tksamc_version',
            field=models.IntegerField(choices=[(1, 'Classic TKSA-MC'), (2, 'GTKSA-MC'), (0, 'Both')], default=1),
        ),
    ]
