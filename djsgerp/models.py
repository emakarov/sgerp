# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class GantryPosition(models.Model):
    lat = models.DecimalField(max_digits=15, decimal_places=12, verbose_name=_("Latitude"), help_text=_("Location in degrees"))
    lon = models.DecimalField(max_digits=15, decimal_places=12, verbose_name=_("Longitude"), help_text=_("Location in degrees"))
    lat2 = models.DecimalField(max_digits=15, decimal_places=12, verbose_name=_("Latitude 2"), help_text=_("Location in degrees"))
    lon2 = models.DecimalField(max_digits=15, decimal_places=12, verbose_name=_("Longitude 2"), help_text=_("Location in degrees"))
    latsvy = models.DecimalField(max_digits=15, decimal_places=8, verbose_name=_("Latitude SVY21"), help_text=_("Location in SVY21"))
    lonsvy = models.DecimalField(max_digits=15, decimal_places=8, verbose_name=_("Longitude SVY21"), help_text=_("Location in SVY21"))
    latsvy2 = models.DecimalField(max_digits=15, decimal_places=8, verbose_name=_("Latitude SVY21"), help_text=_("Location in SVY21"))
    lonsvy2 = models.DecimalField(max_digits=15, decimal_places=8, verbose_name=_("Longitude SVY21"), help_text=_("Location in SVY21"))

    def __unicode__(self):
        return "{}: {}, {}".format(self.id, int(self.latsvy), int(self.lonsvy))


class VehicleType(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return "{}".format(self.name)


class GantryPriceElement(models.Model):
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="Start Time")
    effective_date = models.DateField(verbose_name="Effective date", blank=True, null=True)
    vehicle_type = models.ForeignKey(VehicleType, blank=True, null=True, verbose_name="Vehicle Type")
    zone_id = models.CharField(max_length=10, verbose_name="Zone ID")
    gantry_position = models.ForeignKey(GantryPosition, blank=True, null=True, related_name="prices")
    daytype = models.CharField(max_length=20, verbose_name="Day Type", default="Weekdays")
    charge_amount = models.FloatField(verbose_name="Charge Amount", default=0.0)

    def __unicode__(self):
        return "{}: ${}: {}-{} - {}".format(self.zone_id, self.charge_amount, self.start_time, self.end_time, self.vehicle_type.name)
