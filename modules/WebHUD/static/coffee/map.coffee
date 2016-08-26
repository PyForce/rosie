map = L.map('map',
    crs: L.CRS.Simple
    zoomAnimation: false).setView [0, 0], 9

L.DomUtil.setTransform = (el, offset, scale, angle) ->
    pos = offset || new L.Point 0,0

    translate = if L.Browser.ie3d then "translate(#{pos.x}px,#{pos.y}px)"\
        else "translate3d(#{pos.x}px,#{pos.y}px,0)"
    rotate = if angle then "rotate(#{angle}rad)" else ''
    scl = if scale then "scale(#{scale})" else ''

    el.style[L.DomUtil.TRANSFORM] = "#{translate}#{rotate}#{scl}"

L.DomUtil.setPosition = (el, point, angle) ->
    el._leaflet_pos = point

    if L.Browser.any3d
        L.DomUtil.setTransform el, point, undefined, angle
    else
        el.style.left = "#{point.x}px"
        el.style.top = "#{point.y}px"


class RobotOverlay extends L.ImageOverlay
    constructor: (@_url, latlng, @_width, @_height, options) ->
        @_latlng = L.latLng latlng
        @_angle = 45

        @_recalcBounds()
        L.setOptions @, options

    _recalcBounds: () ->
        x1 = [@_latlng.lat - @_width / 2, @_latlng.lng - @_height / 2]
        x2 = [@_latlng.lat + @_width / 2, @_latlng.lng + @_height / 2]

        @_bounds = L.latLngBounds [x1, x2]

    _reset: () ->
        image = @_image
        bounds = new L.Bounds @_map.latLngToLayerPoint(@_bounds.getNorthWest()),
            @_map.latLngToLayerPoint(@_bounds.getSouthEast())
        size = bounds.getSize()

        point =
            x: (bounds.min.x + bounds.max.x) / 2
            y: (bounds.min.y + bounds.max.y) / 2

        L.DomUtil.setPosition image, point, @_angle
        image.style.width = "#{size.x}px"
        image.style.height = "#{size.y}px"
        image.style.zIndex = '1000'

    setAngle: (@_angle) ->
        @_reset()

    getAngle: () ->
        @_angle

    setLatLng: (latlng) ->
        oldLatLng = @_latlng
        @_latlng = L.latLng latlng

        @_recalcBounds()

        @_reset() if @_map
        if L.DomUtil.TRANSFORM
            # use the CSS transform rule if available
            @_image.style[L.DomUtil.TRANSFORM] += " rotate(#{@options.angle}rad)"

        @fire 'move',
            oldLatLng: oldLatLng
            latLlng: @_latlng

    getLatLng: () ->
        @_latlng


`var themap={
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

var dcolor = 0.25

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
`

# mapLayer = L.geoJson().addTo map
# mapLayer.addData geodata

# trajectory = L.Polyline.Plotter([
#                     [0, 6]
#                 ],
#                 weight: 5
#                 readOnly: true)
#             .addTo map

readOnly = true
$("#i-p2p").click () ->
    readOnly = !readOnly
    trajectory.setReadOnly readOnly
