import sys, inspect
from django.conf.urls import url, include

from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.api import Api
from tastypie.authorization import DjangoAuthorization

from djsgerp.models import GantryPosition, GantryPriceElement

class GantryPriceElementResource(ModelResource):
    class Meta:
        queryset = GantryPriceElement.objects.all()
        resource_name = 'djsgerp/gantrypriceelement'

class GantryPositionResource(ModelResource):
    class Meta:
        queryset = GantryPosition.objects.all() #filter(external_id__isnull=False)
        resource_name = 'djsgerp/gantryposition'

clsmembers = inspect.getmembers(sys.modules[__name__], lambda member: inspect.isclass(member) and member.__module__ == __name__)
api_v1 = Api(api_name='v1')
resources = []
resources = [c[1]() for c in clsmembers]
[api_v1.register(r) for r in resources]
urlpatterns = [
    url(r'^api/', include(api_v1.urls)),
]

