# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djsgerp', '0003_auto_20161119_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='gantrypriceelement',
            name='charge_amount',
            field=models.FloatField(default=0.0, verbose_name='Charge Amount'),
        ),
    ]