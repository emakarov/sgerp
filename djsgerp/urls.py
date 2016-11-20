from django.conf import settings
from django.conf.urls import url
from djsgerp.views import *
from djsgerp.api import urlpatterns as api_patterns

urlpatterns = [
    url(r'vehicle_list_from_logs', vehicle_list_from_logs),
    url(r'vehicle_data', vehicle_data),
    url(r'gantries_2', gantries_2),
    url(r'gantries', gantries),
    url(r'matchmake', matchmake),
    url(r'crossgantry', crossgantry),
    url(r'', index),
]

urlpatterns = api_patterns + urlpatterns
