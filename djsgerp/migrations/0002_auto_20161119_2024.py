# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 20:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djsgerp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GantryPriceElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(verbose_name='Start Time')),
                ('end_time', models.TimeField(verbose_name='Start Time')),
                ('effective_date', models.DateField(blank=True, null=True, verbose_name='Effective date')),
                ('zone_id', models.CharField(max_length=10)),
                ('gantry_position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='djsgerp.GantryPosition')),
            ],
        ),
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='gantrypriceelement',
            name='vehicle_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='djsgerp.VehicleType'),
        ),
    ]
