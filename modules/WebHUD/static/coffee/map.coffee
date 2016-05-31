L = require 'leaflet'

MapActions = require './actions/map'


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
        sw = [@_latlng.lat + @_height / 2, @_latlng.lng - @_width / 2]
        ne = [@_latlng.lat - @_height / 2, @_latlng.lng + @_width / 2]

        @_bounds = L.latLngBounds(sw,ne)

    _reset: () ->
        image = @_image
        bounds = new L.Bounds @_map.latLngToLayerPoint(@_bounds.getNorthWest()),
            @_map.latLngToLayerPoint(@_bounds.getSouthEast())
        size = bounds.getSize()

        point =
            x: (bounds.min.x)
            y: (bounds.min.y)

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


drawMap = (lmap) ->
    map_style =
        borders:
            color: 'rgba(0, 0, 255, 0.25)'
            weight: 0
        walls:
            color: '#101010'
            weight: 5
        doors:
            color: '#0000ef'
            weight: 10
            opacity: 0.5
        items:
            color: '#0f0f0f'
            weight: 1
            opacity: 0.75
    dcolor = .25

    for room of lmap.rooms
        do (room) ->
            for elements of lmap.rooms[room]
                if elements is 'borders'
                    border_style =
                        color: "rgba(0, 0, 255, #{dcolor})"
                        weight: 0
                    L.geoJson(lmap.rooms[room][elements], style: border_style)
                        .addTo map
                    dcolor += 0.25
                    if dcolor > .8
                        dcolor = .25
                else if elements is 'items'
                    L.geoJson(lmap.rooms[room][elements][item],
                        style: map_style[elements]).addTo map\
                            for item of lmap.rooms[room][elements]
                else
                    L.geoJson(lmap.rooms[room][elements],
                              style: map_style[elements]).addTo map


map.on 'click', (e) ->
    MapActions.click e.latlng


module.exports =
  RobotOverlay: RobotOverlay
  map: map
  drawMap: drawMap
