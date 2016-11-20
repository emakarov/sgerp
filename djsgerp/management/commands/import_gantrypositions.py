# -*- coding: utf-8
from __future__ import print_function, unicode_literals

import shapefile
import pyproj

from django.core.management.base import BaseCommand
from django.conf import settings

from djsgerp.models import GantryPosition

svy21 = r'+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs'

class Command(BaseCommand):

    def handle(self, *args, **options):
        sf = shapefile.Reader(settings.GANTRY_FILE)
        p = pyproj.Proj(svy21)
        shapes = sf.shapes()

        for s in shapes:
            x, y = s.points[0]
            x2, y2 = s.points[1]
            lon, lat = p(x, y, inverse=True)
            lon2, lat2 = p(x2, y2, inverse=True)
            gp = GantryPosition()
            gp.lat = lat
            gp.lon = lon
            gp.lat2 = lat2
            gp.lon2 = lon2
            gp.latsvy = y
            gp.lonsvy = x
            gp.latsvy2 = y2
            gp.lonsvy2 = x2
            gp.save()
