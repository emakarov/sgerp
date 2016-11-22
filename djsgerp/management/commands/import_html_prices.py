# -*- coding: utf-8
from __future__ import print_function, unicode_literals

import os

from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import time

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.urltemplate_base = 'https://www.mytransport.sg/mapapp/pages/ddls/{}_ddl.html'
        self.urltemplate_price = 'https://www.mytransport.sg/mapapp/pages/tables/{}_table_{}.html'
        self.output_filename_gantry = 'gantry_{}.html'
        self.output_filename_vehiclekind = 'gantry_{}_vehiclekind_{}.html'

        self.vehicle_kinds = {
          'Cars/Light Goods/Taxi': {
               'Weekdays': '0',
               'Saturday': '1',
          },
          'Motorcycles': {
               'Weekdays': '2',
               'Saturday': '3',
          },
          'Heavy Goods/Small Buses': {
               'Weekdays': '4',
               'Saturday': '5',
          },
          'Very Heavy Goods/Big Buses': {
               'Weekdays': '6',
               'Saturday': '7',
          },
        }

        for s in range(68, 94):
            resp = requests.get(self.urltemplate_base.format(s))
            filename = os.path.join(settings.HTML_PRICES_DIR, self.output_filename_gantry.format(s))
            f = open(filename, 'w')
            f.write(resp.content)
            f.close()
            for vk in self.vehicle_kinds:
                for day in self.vehicle_kinds[vk]:
                    dayval = self.vehicle_kinds[vk][day]
                    print(s, dayval)
                    resp = requests.get(self.urltemplate_price.format(s, dayval))
                    filename = os.path.join(settings.HTML_PRICES_DIR, self.output_filename_vehiclekind.format(s, dayval))
                    f = open(filename, 'w')
                    f.write(resp.content)
                    f.close()
                    time.sleep(1)
            time.sleep(5)
                    
