# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 09:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GantryPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.DecimalField(decimal_places=12, help_text='Location in degrees', max_digits=15, verbose_name='Latitude')),
                ('lon', models.DecimalField(decimal_places=12, help_text='Location in degrees', max_digits=15, verbose_name='Longitude')),
                ('lat2', models.DecimalField(decimal_places=12, help_text='Location in degrees', max_digits=15, verbose_name='Latitude 2')),
                ('lon2', models.DecimalField(decimal_places=12, help_text='Location in degrees', max_digits=15, verbose_name='Longitude 2')),
                ('latsvy', models.DecimalField(decimal_places=8, help_text='Location in SVY21', max_digits=15, verbose_name='Latitude SVY21')),
                ('lonsvy', models.DecimalField(decimal_places=8, help_text='Location in SVY21', max_digits=15, verbose_name='Longitude SVY21')),
                ('latsvy2', models.DecimalField(decimal_places=8, help_text='Location in SVY21', max_digits=15, verbose_name='Latitude SVY21')),
                ('lonsvy2', models.DecimalField(decimal_places=8, help_text='Location in SVY21', max_digits=15, verbose_name='Longitude SVY21')),
            ],
        ),
    ]
