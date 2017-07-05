import os
from os.path import isfile, join
import json
import csv
import pyproj
import shapefile
import datetime

import utm
from mapbox import MapMatcher
from shapely.geometry import Point, LineString
import numpy as np

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse

from djsgerp.models import GantryPosition, GantryPriceElement, VehicleType

svy21 = r'+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs'


def index(request):
    """index file"""
    return render(request, 'djsgerp/index.html', {})


def vehicle_list_from_logs(request):
    logs = [f for f in os.listdir(settings.VEHICLE_LOGS_DIR) if isfile(join(settings.VEHICLE_LOGS_DIR, f))]
    return JsonResponse({'vehicles': logs})


def vehicle_data(request):
    v = request.GET['q']
    f = os.path.join(settings.VEHICLE_LOGS_DIR, v)
    pts = []
    with open(f, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        reader.next()
        for row in reader:
            pts.append({
                'ts': row[0],
                'lat': row[1],
                'lon': row[2],
            })
    return JsonResponse({'data': pts})


def gantries(request):
    sf = shapefile.Reader(settings.GANTRY_FILE)
    p = pyproj.Proj(svy21)
    shapes = sf.shapes()
    pts = []
    for s in shapes:
        x, y = s.points[0]
        x2, y2 = s.points[1]
        lon, lat = p(x, y, inverse=True)
        lon2, lat2 = p(x2, y2, inverse=True)
        pts.append({
          0: {'lat': lat, 'lon': lon},
          1: {'lat': lat2, 'lon': lon2},
        })
    return JsonResponse({'data': pts})

def gantries_2(request):
    f = open(settings.ERP_GEODATA)
    erp_geodata = json.loads(f.read())
    erp_geodata_gantries = erp_geodata['SERVICESINFO'][0]['ERPINFO']
    ext_gantries = []
    p = pyproj.Proj(svy21)
    features = []
    for e in erp_geodata_gantries:
        if 'ZONEID' in e:
            x = e['X_ADDR']
            y = e['Y_ADDR']
            lon, lat = p(x, y, inverse=True)
            feature = {
                "type": "Feature",
                "properties": {
                    "zone_id": e['ZONEID']
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }            
            }
            features.append(feature)
    geojson = {
        "type": "FeatureCollection",
        "features": features
    } 
    return JsonResponse(geojson)

def listindex(list, elem):
    try:
        return list.index(elem)
    except:
        return None


def matchmake(request):
    v = request.GET['q']
    corrected_res, corrected_coords, corrected_complete_times = matchmake_fn(v)
    return JsonResponse({'data': corrected_res})


def crossgantry(request):
    v = request.GET['q']
    corrected_res, corrected_coords, corrected_complete_times = matchmake_fn(v)
    prev = None
    gantrypositions = GantryPosition.objects.all()
    prev_g = None
    gantrycache = []
    gantryidx = []
    gantrylatlons = []
    vehicle_type = VehicleType.objects.get(name='Heavy Goods/Small Buses')
    daytype = 'Weekdays'
    for g in gantrypositions:
        p1 = (utm.from_latlon(g.lat, g.lon)[0], utm.from_latlon(g.lat, g.lon)[1])
        p2 = (utm.from_latlon(g.lat2, g.lon2)[0], utm.from_latlon(g.lat2, g.lon2)[1])
        gantryline = LineString([p1, p2])
        gantrycache.append(gantryline)
        gantryidx.append(g.id)
        gantrylatlons.append({'lat': (g.lat + g.lat2)/2, 'lon': (g.lon + g.lon2)/2})
    gantrycrosses = []
    charge_total = 0.
    for c in corrected_res:
        if prev is not None:
            p1 = (utm.from_latlon(c['lat'], c['lon'])[0], utm.from_latlon(c['lat'], c['lon'])[1])
            p2 = (utm.from_latlon(prev['lat'], prev['lon'])[0], utm.from_latlon(prev['lat'], prev['lon'])[1])
            line = LineString([p1, p2])
            intersects = [line.intersects(x) for x in gantrycache]
            idx_intersects = [i for i in range(len(intersects)) if intersects[i]]
            if idx_intersects:
                gantry_id = gantryidx[idx_intersects[0]]
                gantry_pos = gantrylatlons[idx_intersects[0]]
                y = (c['utsc'] + prev['utsc']) * 0.5
                times = datetime.datetime.fromtimestamp(int(y))
                price = None
                try:
                    price = GantryPriceElement.objects.get(gantry_position=gantry_id, start_time__lte=times, end_time__gte=times, vehicle_type=vehicle_type, daytype=daytype).charge_amount
                    charge_total += price
                except:
                    pass
                gantrycrosses.append({'gantry_id': gantry_id, 'gantry_position': gantry_pos, 'b': c, 'a': prev, 'charged': price})
        prev = c
    return JsonResponse({'data': gantrycrosses, 'charge_estimation': charge_total})


def matchmake_fn(v):
    # returns matched points and approximated time along the curve
    f = os.path.join(settings.VEHICLE_LOGS_DIR, v)
    pts = []
    f_cor = os.path.join(settings.VEHICLE_LOGS_DIR, 'corrected/' + v)
    with open(f, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        reader.next()
        for row in reader:
            pts.append({
                'ts': row[0],
                'lat': row[1],
                'lon': row[2],
            })
    parts = len(pts)/100
    corrected_coords = []
    proceed = True
    i = 0
    feature_idx = 0
    corrected_complete_times = []
    while len(pts[i*100:i*100+100]) > 0:
        sub_pts = pts[i*100:i*100+100]
        try:
            corrected = correct(sub_pts, v, i)
        except:
            return [], [], []
        feature_idx = 0
        for feature in corrected:
            matched_points = feature['properties']['matchedPoints']
            indices = feature['properties']['indices']
            corrected_line_pts_timed = []
            prev_matched_idx = None
            times_detected = []
            prev_matched_idx = None
            prev_matched_pts = None
            for idxc, c in enumerate(feature['geometry']["coordinates"]):
                matched_point_idx = listindex(matched_points, c)
                corrected_coords += [c]
                corrected_coords[len(corrected_coords)-1].append(None)
                corrected_coords[len(corrected_coords)-1].append(None)
                if matched_point_idx is not None:
                    orig_pts_idx = indices[matched_point_idx]
                    corrected_coords[len(corrected_coords)-1][2] = sub_pts[orig_pts_idx]['ts']
                    # TODO need to be converted to UTC first
                    uts = (datetime.datetime.strptime(sub_pts[orig_pts_idx]['ts'],'%Y-%m-%d %H:%M:%S') - datetime.datetime(1970, 1, 1)).total_seconds()
                    corrected_coords[len(corrected_coords)-1][3] = uts
        i += 1
    prev_idx = None
    corrected_complete_times = []
    for idx, c in enumerate(corrected_coords):
        corrected_complete_times.append(c[2])
        if c[2] is not None:
            ts_detected = c[3] # unix timestamp
            if prev_idx is not None:
                corrected_coords_part = corrected_coords[prev_idx:idx+1]
                corrected_line_pts = [(utm.from_latlon(x[1], x[0])[0], utm.from_latlon(x[1], x[0])[1]) for x in corrected_coords_part]
                corrected_line = LineString(corrected_line_pts)
                lengths_corrected = [corrected_line.project(Point(utm.from_latlon(x[1], x[0])[0],utm.from_latlon(x[1], x[0])[1])) for x in corrected_coords_part]
                times_detected = [prev_ts_detected, ts_detected]
                lengths_time_detected = [0, corrected_line.length]
                # approximation of time along the curve
                times_interpolated = np.interp(lengths_corrected, lengths_time_detected, times_detected)
                corrected_complete_times[prev_idx:idx+1] = [t for t in times_interpolated]
            prev_idx = idx
            prev_ts_detected = ts_detected
    corrected_res = [] 
    map(lambda x, y: corrected_res.append({'lat': x[1], 'lon': x[0], 'ts': x[2], 'uts': x[3], 'utsc': y, 'tsc': datetime.datetime.fromtimestamp(int(y))}), corrected_coords, corrected_complete_times)
    return corrected_res, corrected_coords, corrected_complete_times


def correct(pts, v, i):
    f_cor = os.path.join(settings.VEHICLE_LOGS_DIR, 'corrected/{}.{}'.format(v, i))
    # load result from simple cache
    if os.path.isfile(f_cor):
        file = open(f_cor, 'r')
        corrected = json.loads(file.read())['features']
        return corrected
    coord_times = [datetime.datetime.strptime(x['ts'],'%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%dT%H:%M:%SZ") for x in pts]
    coordinates = [[float(x['lon']), float(x['lat'])] for x in pts]
    line = {
        "type": "Feature",
        "properties": {
            "coordTimes": coord_times
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        }
    }
    print(coordinates)

    service = MapMatcher(access_token=settings.MAPBOX_KEY)
    response = service.match(line, profile='mapbox.driving')
    print(response, response.geojson())
    corrected = response.geojson()['features']
    # save result to simple file cache
    file = open(f_cor, 'w')
    file.write(json.dumps(response.geojson()))
    file.close()
    return corrected
