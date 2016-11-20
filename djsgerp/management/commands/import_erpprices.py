# -*- coding: utf-8
from __future__ import print_function, unicode_literals

import json

from django.core.management.base import BaseCommand
from django.conf import settings

from djsgerp.models import GantryPriceElement, VehicleType


class Command(BaseCommand):

    def handle(self, *args, **options):
        f = open(settings.ERP_RATES_FILE)
        rates = json.loads(f.read())

        for r in rates:
            vehicle_type, created = VehicleType.objects.get_or_create(name=r['VehicleType'])
            gpe = GantryPriceElement()
            gpe.start_time = r['StartTime']
            gpe.end_time = r['EndTime']
            gpe.vehicle_type = vehicle_type
            gpe.charge_amount = float(r['ChargeAmount'])
            gpe.daytype = r['DayType']
            gpe.effective_date = r['EffectiveDate']
            gpe.zone_id = r['ZoneID']
            gpe.save()
