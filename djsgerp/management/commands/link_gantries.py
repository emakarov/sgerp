# -*- coding: utf-8
from __future__ import print_function, unicode_literals

import json
import pyproj
from shapely.geometry import Point, LineString
import numpy as np

from django.core.management.base import BaseCommand
from django.conf import settings

from djsgerp.models import GantryPosition, GantryPriceElement, VehicleType

svy21 = r'+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs'

class Command(BaseCommand):

    def handle(self, *args, **options):
        f = open(settings.ERP_GEODATA)
        erp_geodata = json.loads(f.read())
        gantries = GantryPosition.objects.all()
        gantries_cache = []
        gantries_ids = []

        for g in gantries:
            a = (utm.from_latlon(g.lat, g.lon)[0], utm.from_latlon(g.lat, g.lon)[1])
            b = (utm.from_latlon(g.lat2, g.lon2)[0], utm.from_latlon(g.lat2, g.lon2)[1])  
            line = LineString([a, b])
            gantries_cache.append(line)
            gantries_ids.append(g.id)

        erp_geodata_gantries = erp_geodata['SERVICESINFO'][0]['ERPINFO']
        ext_gantries = []
        p = pyproj.Proj(svy21)

        for e in erp_geodata_gantries:
            if 'ZONEID' in e:
                x = e['X_ADDR']
                y = e['Y_ADDR']
                lon, lat = p(x, y, inverse=True)
                gpe = GantryPriceElement.objects.filter(zone_id=e['ZONEID'])
                print(gpe.count(), e['ZONEID'])
