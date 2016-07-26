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

        L.DomUtil.setPosition image, bounds.min, @_angle
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


`var geodata = {
    "type": "FeatureCollection",
    "features": [

        {
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
            },
            "properties": {
                "name": "Living Room"
            }
        },

        {
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
            },
            "properties": {
                "name": "Hall"
            }
        },

        {
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
            },
            "properties": {
                "name": "Dinner Room"
            }
        },

        {
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
            },
            "properties": {
                "name": "Kitchen"
            }
        }
    ]
}`

mapLayer = L.geoJson().addTo map
mapLayer.addData geodata

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
