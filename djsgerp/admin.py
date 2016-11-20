# -*- coding: utf-8
from django.contrib import admin

from djsgerp.models import *

class GantryPriceElementInline(admin.TabularInline):
    parent_link = 'gantryposition'
    model = GantryPriceElement

class GantryPositionAdmin(admin.ModelAdmin):
    model = GantryPosition

    inlines = [
        GantryPriceElementInline,
    ]


class VehicleTypeAdmin(admin.ModelAdmin):
    model = VehicleType


class GantryPriceElementAdmin(admin.ModelAdmin):
    model = GantryPriceElement


admin.site.register(GantryPosition, GantryPositionAdmin)
admin.site.register(VehicleType, VehicleTypeAdmin)
admin.site.register(GantryPriceElement, GantryPriceElementAdmin)


