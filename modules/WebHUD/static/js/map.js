var map = L.map('map', {
    crs: L.CRS.Simple,
    zoomAnimation: false
}).setView([1, 2], 7.5);

var imageUrl = "static/images/LTL.svg";

var width = 0.43;
var height = 0.25;
var coords = [0, 0];

L.DomUtil.setTransform = function(el, offset, scale, angle) {
    var pos = offset || new L.Point(0, 0);

    el.style[L.DomUtil.TRANSFORM] =
        (L.Browser.ie3d ?
        'translate(' + pos.x + 'px,' + pos.y + 'px)' :
        'translate3d(' + pos.x + 'px,' + pos.y + 'px,0)') +
        (angle ? ' rotate(' + angle + 'rad)' : '') +
        (scale ? ' scale(' + scale + ')' : '');
};

L.DomUtil.setPosition = function(el, point, angle) { // (HTMLElement, Point[, Boolean])

    /*eslint-disable */
    el._leaflet_pos = point;
    /*eslint-enable */

    if (L.Browser.any3d) {
        L.DomUtil.setTransform(el, point, undefined, angle);
    } else {
        el.style.left = point.x + 'px';
        el.style.top = point.y + 'px';
    }
}

L.MyImageOverlay = L.ImageOverlay.extend({

    initialize: function(imageUrl, latlng, width, height, options) {
        this._url = imageUrl;
        this._latlng = L.latLng(latlng);
        this._width = width;
        this._height = height;
        this._angle = 45;

        this._recalcBounds();
        L.setOptions(this, options);

    },


    _recalcBounds: function() {
        var x1 = [this._latlng.lat - this._width / 2, this._latlng.lng - this._height / 2];
        var x2 = [this._latlng.lat + this._width / 2, this._latlng.lng + this._height / 2];

        var bounds = [x1, x2];

        this._bounds = L.latLngBounds(bounds);
    },

    _reset: function() {
        var image = this._image,
            bounds = new L.Bounds(
                this._map.latLngToLayerPoint(this._bounds.getNorthWest()),
                this._map.latLngToLayerPoint(this._bounds.getSouthEast())),
            size = bounds.getSize();

        L.DomUtil.setPosition(image, bounds.min, this._angle);

        image.style.width = size.x + 'px';
        image.style.height = size.y + 'px';
    },

    setAngle: function(angle) {
        this._angle = angle;

        this._reset();
    },

    getAngle: function(angle) {
        return _angle;
    },

    setLatLng: function(latlng) {
        var oldLatLng = this._latlng;
        this._latlng = L.latLng(latlng);

        this._recalcBounds();

        if (this._map) {
            this._reset();
        }

        if (L.DomUtil.TRANSFORM) {
            // use the CSS transform rule if available
            this._image.style[L.DomUtil.TRANSFORM] += ' rotate(' + this.options.angle + 'rad)';
        }

        return this.fire('move', {
            oldLatLng: oldLatLng,
            latlng: this._latlng
        });
    },

    getLatLng: function() {
        return this._latlng;
    }
})

L.myImageOverlay = function(imageUrl, coords, width, height, options) {
    return new L.MyImageOverlay(imageUrl, coords, width, height, options);
}

var themap={
    "name" : "Gustavo's House",
    "version" : 0.95,
    "rooms" : {

        "Living Room" : {
            "borders" : {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [0.0, 0.0],
                            [0.0, 2.38],
                            [2.63, 2.38],
                            [2.63, 0.96],
							[2.78, 0.0]
                        ]
                    ]
                }
            },
            "walls" : {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [
                        [
                            [0.0, 1.28],
                            [0.0, 0.0],
                            [1.98, 0.0]
                        ],
                        [
                            [0.0, 2.16],
                            [0.0, 2.38],
                            [2.63, 2.38],
                            [2.63, 0.96]
                        ]
                    ]
                }                
            },
            "doors" : {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [
						[
                            [0.0, 1.28],
                            [0.0, 2.16]
						],
                        [
                            [1.98, 0,0],
                            [2.78, 0.0],
                        ]
					]
                }
            },
            "items" : {
				"chair1": {
					"type": "Feature",
					"geometry": {
						"type": "Polygon",
						"coordinates": [
							[
								[1.9, 1.75],
								[1.9, 2.25],
								[2.4, 2.25],
								[2.4, 1.75]
							]
						]
					}
				},
				"chair2": {
					"type": "Feature",
					"geometry": {
						"type": "Polygon",
						"coordinates": [
							[
								[1.2, 1.75],
								[1.2, 2.25],
								[1.7, 2.25],
								[1.7, 1.75]
							]
						]
					}
				}
            }
        },

        "Hall" : {
            "borders" : {
				"type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
						[
                            [2.63, 0.96],
                            [3.34, 0.96],
                            [3.43, 0.23],
                            [3.10, 0.23],
							[3.10, 0.0],
							[2.78, 0.0]
                        ]
					]
                }
            },
            "walls" : {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [
                        [
                            [2.63, 0.96],
                            [3.34, 0.96]
                        ],
                        [
                            [2.78, 0.0],
                            [3.10, 0.0],
                            [3.10, 0.23],
                            [3.43, 0.23]
                        ]
                    ]
                }            
            },
            "doors" : {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": []
                }                
            },
            "items" : {
				"obj": {
					"type": "Feature",
					"geometry": {
						"type": "MultiLineString",
						"coordinates": []
					}
				}
            }
        },

        "Dinning Room" : {
            "borders" : {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
						[							
							[3.43, 0.0],
							[3.43, 0.23],
                            [3.34, 0.96],				
                            [3.34, 2.38],							
                            [5.47, 2.38],							
                            [5.47, 2.28],							
                            [5.82, 2.28],
                            [5.82, 2.38],
                            [7.16, 2.38],
							[7.16, 0.22],
                            [6.85, 0.22],
							[6.25, 0.16],
                            [5.86, 0.0]
                        ]
					]
                }
            },
            "walls" : {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [
                        [
                            [3.34, 0.96],
                            [3.34, 2.38],
                            [5.47, 2.38],
                            [5.47, 2.28],
                            [5.82, 2.28],
                            [5.82, 2.38],
                            [7.16, 2.38]
                        ],
                        [
                            [3.43, 0.23],
                            [3.43, 0.0],
                            [5.86, 0.0],
                            [6.25, 0.16]
                        ],
                        [
                            [6.85, 0.22],
                            [7.16, 0.22],
                            [7.16, 1.49]
                        ]
                    ]
                } 
            },
            "doors" : {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [
						[
                            [6.85, 0.22],
							[6.25, 0.16]
						]
					]
                }                
            },
            "items" : {
				"refrigerator": {
					"type": "Feature",
					"geometry": {
						"type": "Polygon",
						"coordinates": [
							[
								[5.9, 1.75],
								[5.9, 2.3],
								[6.5, 2.3],
								[6.5, 1.75]
							]
						]
					}
				},
				"table": {
					"type": "Feature",
					"geometry": {
						"type": "Polygon",
						"coordinates": [
							[
								[3.9, 1.0],
								[3.9, 1.9],
								[5.2, 1.9],
								[5.2, 1.0]
							]
						]
					}
				}
            }
        },

        "Kitchen" : {
            "borders" : {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
						[	
							[7.16, 2.38],
							[7.16, 1.49],
							[7.22, 1.49],
							[7.22, 0.22],
							[8.24, 0.22],
							[8.24, 2.38]
                        ]
					]
                }
            },
            "walls" : {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [7.16, 1.49],
                        [7.22, 1.49],
                        [7.22, 0.22],
                        [8.24, 0.22],
                        [8.24, 2.38],
                        [7.16, 2.38]
                    ]
                }
            },
            "doors" : {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": []
                }                
            },
            "items" : {
				"table": {
					"type": "Feature",
					"geometry": {
						"type": "Polygon",
						"coordinates": [
							[
								[7.35, 0.3],
								[7.35, 0.9],
								[8.1, 0.9],
								[8.1, 0.3]
							]
						]
					}
				}          
            }
        }
    }
}
var map_style = {
    'borders' : {
        "color": "rgba(0,0,255,0.25)",
        "weight": 0,
    },
    'walls' : {
        "color": "#101010",
        "weight": 5,
    },
    'doors' : {
        "color": "#0000ef",
        "weight": 10,
        "opacity": 0.5
    },
    'items' : {
        "color": "#0f0f0f",
        "weight": 1,
        "opacity": 0.75
    }
}

// Here goes the function

var dcolor=0.25;

for (var rkey in themap["rooms"]){
    for (ikey in themap["rooms"][rkey]){
		console.log(ikey)
		if (ikey=="borders"){
			var border_style={
				"color": "rgba(0,0,255,"+(dcolor).toString()+")",
				"weight": 0,
			};
			L.geoJson(themap["rooms"][rkey][ikey],{style: border_style}).addTo(map);
			dcolor+=0.25;
			if (dcolor>0.8){
				dcolor=0.25;
			}
		}
		else if (ikey=="items"){
			for (okey in themap["rooms"][rkey][ikey]){
				L.geoJson(themap["rooms"][rkey][ikey][okey],{style: map_style[ikey]}).addTo(map);
			}
		}
		else{
			L.geoJson(themap["rooms"][rkey][ikey],{style: map_style[ikey]}).addTo(map);
		}
    }
}
// Here ends the function




car = L.myImageOverlay(imageUrl, coords, width, height).addTo(map);
trajectory = L.Polyline.Plotter([
    [0, 6]
], {
    weight: 5,
    readOnly: true,
}).addTo(map);

getOdometry(undefined, function(pos){
    car.setLatLng([pos.x, pos.y]);
    car.setAngle(pos.theta);
});

var readOnly = true;

$("#i-p2p").click(function() {
    readOnly = !readOnly;
    trajectory.setReadOnly(readOnly);
});
