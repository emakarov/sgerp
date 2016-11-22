var mapboxgl = require('mapbox-gl');
var $ = require('jquery');
var Backbone = require('backbone');

var app = {};
app.collections = {};
app.map = {};

mapboxgl.accessToken = 'pk.eyJ1IjoiZW1ha2Fyb3YiLCJhIjoiMDFER0JicyJ9.0yaID4RS09gxfY4uyERhVQ';

var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v9',
    center: [103.8198, 1.3521],
    zoom: 11
});
app.map = map;

app.collections['vehicles'] = new Backbone.Collection();
app.collections['gantries'] = new Backbone.Collection();
app.collections['gantrycrosses'] = new Backbone.Collection();

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

var GantryCross = Backbone.Model.extend({
    zoomto: function(_map) {
      var coordinates = [parseFloat(this.attributes.gantry_position.lon), parseFloat(this.attributes.gantry_position.lat)];
      _map.flyTo({center: coordinates, zoom: 18});
    }
});

var GantryPosition = Backbone.Model.extend({

  add_data: function(){
    this.attributes.pts = pts;
    this.attributes.coordinates = new Array();
    this.attributes.coordinates.push([pts[0].lon, pts[0].lat]);
    this.attributes.coordinates.push([pts[1].lon, pts[1].lat]);
  },
  get_coordinates: function(){
    var coords = new Array();
    var at = this.attributes;
    coords.push( [parseFloat(at.lon), parseFloat(at.lat)] );
    coords.push( [parseFloat(at.lon2), parseFloat(at.lat2)] );
    return coords;
  },
  show: function(_map){

    _map.addSource( this.cid, {
      "type": "geojson",
      "data": {
          "type": "Feature",
          "properties": {
            "id": this.attributes.id
          },
          "geometry": {
            "type": "LineString",
            "coordinates": this.get_coordinates()
          }
      }
    }); 

    _map.addLayer({
        "id": this.cid,
        "type": "line",
        "source": this.cid,
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        "paint": {
            "line-color": "#ff0000",
            "line-width": 4
        }
     });

    _map.addLayer({
        "id": this.cid + "title",
        "type": "symbol",
        "source": this.cid,
        "layout": {
            "text-field": "{id}",
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-offset": [0.1, 0.8],
            "text-anchor": "bottom"
        }
    });



  }

});

var Vehicle = Backbone.Model.extend({
  add_data: function(data){
     this.attributes.data = data;
     this.attributes.coordinates = new Array();
     for (var d in data){
         this.attributes.coordinates.push([parseFloat(data[d]["lon"]), parseFloat(data[d]["lat"])]);
     }
    
  },
  show_track: function(_map) {
      _map.addSource( this.attributes.id, {
          "type": "geojson",
          "data": {
              "type": "Feature",
              "properties": {},
              "geometry": {
                  "type": "LineString",
                  "coordinates": this.attributes.coordinates
               }
          }
      });

      _map.addLayer({
        "id": this.attributes.id,
        "type": "line",
        "source": this.attributes.id,
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        "paint": {
            "line-color": getRandomColor(),
            "line-width": 6
        }
      });

  },
  show_track_data: function(data, _map){
    $('#'+this.cid+'_showmapbtn').html("Hide track");
    var layer = _map.getLayer(this.attributes.id);
    if (layer === undefined){
      this.add_data(data);
      this.show_track(_map);
    } else {
      _map.setLayoutProperty(this.attributes.id, 'visibility', 'visible');
    }
  },
  hide_track_data: function(_map) {
    this.attributes.shown_track = false;
    _map.setLayoutProperty(this.attributes.id, 'visibility', 'none');
    $('#'+this.cid+'_showmapbtn').html("Show track");
  }
})

map.on('load', function() {

  $.get('/erp/vehicle_list_from_logs/', function(data) {
    var vehicles = data.vehicles;
    for (var v in vehicles){
      var vehicle = new Vehicle({id: vehicles[v]});
      app.collections['vehicles'].add(vehicle);
      var line = '<div style="padding:5px;border-bottom:1px solid #eee;font-size:11px;"><div>' + vehicles[v] + '</div>';
      line += '<div><span id="'+vehicle.cid+'_showmapbtn" class="cursored" onclick="app.showtrack(this, \''+vehicles[v]+'\')" style="margin-right:20px">Show track</span>'
      line += '<span class="cursored" onclick="app.showerpcost(\''+vehicles[v]+'\')">ERP cost</span></div></div>';
      $("#vehicle_logs_list").append(line);
    }
  });

  $.get('/erp/api/v1/djsgerp/gantryposition/?format=json&limit=0', function(data) {

      for (var i in data.objects){
        var g = new GantryPosition(data.objects[i]);
        app.collections['gantries'].add(g);
        g.show(map);
      }      
  
  });

  map.addSource('ext_gantries', {
    type: 'geojson',
    data: '/erp/gantries_2/'
  });

  map.addLayer({
        "id": "ext_gantries",
        "source": "ext_gantries",
        "type": 'circle',
        "paint": {
            "circle-radius": 10,
            "circle-color": '#007cbf'
          }
  });

    map.addLayer({
        "id": "ext_gantries_zones",
        "type": "symbol",
        "source": "ext_gantries",
        "layout": {
            "text-field": "{zone_id}",
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-offset": [0, 0.6],
            "text-anchor": "top"
        }
    });

});

app.showtrack = function(el, f){
  if ( $(el).hasClass('disabled') ){
    return;
  }
  $(el).addClass('disabled');
  if ( app.collections['vehicles'].where({'id':f})[0].attributes.shown_track != true) {
    app.collections['vehicles'].where({'id':f})[0].attributes.shown_track = true;
    $.get('/erp/matchmake/?q='+f, function(data) {
      $(el).removeClass('disabled');
      app.collections['vehicles'].where({'id':f})[0].show_track_data(data.data, app.map);
    });
  } else {
    $(el).removeClass('disabled');
    app.collections['vehicles'].where({'id':f})[0].hide_track_data(app.map);  
  }
}

app.showerpcost = function(f){
  $("#erp_box_holder").show();
  $.get('/erp/crossgantry/?q='+f, function(data){
    $("#vehicle_id_erp_holder").html(f);
    for (var i in data.data) {
      var gc = new GantryCross(data.data[i]);
      app.collections['gantrycrosses'].add(gc);
      var line = '<div><div class="cursored col-xs-10" style="padding:5px" onclick="app.showgantrycross(\''+gc.cid+'\')"> Gantry ID ';
      line += data.data[i]['gantry_id'] + ' at ' + data.data[i]['a']['tsc'] + ' and ' + data.data[i]['b']['tsc'] + '</div>';
      line += '<div class="col-xs-2">$'+ data.data[i].charged + '</div></div>';
      $("#erp_crosses_holder").append(line);
    }
    var line = '<div class="col-xs-12" style="padding:5px">Total charge estimation: $' + data.charge_estimation + '</div>';
    $("#erp_crosses_holder").append(line);
  });

}

app.closeerpbox = function(){
  $("#erp_crosses_holder").html("");
  $("#vehicle_id_erp_holder").html("");
  $("#erp_box_holder").hide();
}

app.showgantrycross = function(cid) {
  var gc = app.collections['gantrycrosses'].get({"cid": cid});
  gc.zoomto(map);
}

window.app = app;
window.$ = $;
