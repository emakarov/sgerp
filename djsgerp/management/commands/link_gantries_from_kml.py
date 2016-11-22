# -*- coding: utf-8
from __future__ import print_function, unicode_literals

import json
import pyproj
from shapely.geometry import Point, LineString
import numpy as np
import utm
from pykml import parser
from pykml.factory import KML_ElementMaker as KML

from django.core.management.base import BaseCommand
from django.conf import settings

from djsgerp.models import GantryPosition, GantryPriceElement, VehicleType


class Command(BaseCommand):

    def handle(self, *args, **options):
        f = open(settings.GANTRY_KML)
        erp_kml = f.read()
        gantries = GantryPosition.objects.all()
        gantries_cache = []
        gantries_objs = []
        root = parser.fromstring(erp_kml)
        f.close()

        for g in gantries:
            a = (utm.from_latlon(g.lat, g.lon)[0], utm.from_latlon(g.lat, g.lon)[1])
            b = (utm.from_latlon(g.lat2, g.lon2)[0], utm.from_latlon(g.lat2, g.lon2)[1])  
            line = LineString([a, b])
            gantries_cache.append(line)
            gantries_objs.append(g)

        ext_gantries = []
        ext_gantries_names = []
        ext_gantries_ids = []
        for p in root.Document.Placemark:
            x = p.Point.coordinates
            lon, lat = tuple([float(y) for y in x.text.replace('\n\t\t\t','').replace(',0\n\t\t', '').split(',')])
            pt = Point(utm.from_latlon(lat, lon))
            name = p.name.text.split('<td>')[1].split('</td>')[0]
            ext_gantries_id = p.description.text.split('/ddls/')[1].split('_ddl')[0]
            distances = [gc.distance(pt) for gc in gantries_cache]
            min_idx = distances.index(min(distances))
            gantry = gantries_objs[min_idx]
            gantry.name = name
            gantry.external_id = ext_gantries_id
            gantry.save()
