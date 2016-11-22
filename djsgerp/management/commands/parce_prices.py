# -*- coding: utf-8
from __future__ import print_function, unicode_literals

import os

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.conf import settings

from djsgerp.models import GantryPosition, GantryPriceElement, VehicleType


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.vehicle_kinds = settings.VEHICLE_KINDS
        self.output_filename_vehiclekind = 'gantry_{}_vehiclekind_{}.html'

        gantries = GantryPosition.objects.filter(external_id__isnull=False)
        for g in gantries:
            s = g.external_id
            for vk in self.vehicle_kinds:
                for day in self.vehicle_kinds[vk]:
                    dayval = self.vehicle_kinds[vk][day]
                    filename = os.path.join(settings.HTML_PRICES_DIR, self.output_filename_vehiclekind.format(s, dayval))
                    soup = BeautifulSoup(open(filename))
                    rows = soup.findAll("table", { "class" : "styler" })[0].findAll('tr')
                    for tr in rows:
                        time_interval = tr.findAll('td')[0].text
                        try:
                            start_time = time_interval.split(' - ')[0]
                            end_time = time_interval.split(' - ')[1]
                            gpe = GantryPriceElement()
                            gpe.start_time = start_time
                            gpe.end_time = end_time
                            gpe.gantry_position = g
                            gpe.daytype = day
                            gpe.vehicle_type, created = VehicleType.objects.get_or_create(name=vk)
                            gpe.charge_amount = float(tr.findAll('td')[1].text.replace('$',''))
                            gpe.save()
                        except Exception as e:
                            print(e)
