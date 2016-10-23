$ = jQuery = require 'jquery'

{RobotOverlay, drawMap, map} = require './map'


DEBUG = true


# Class that wraps robot communication
class Robot
    constructor: (info) ->
        @host = document.domain
        @port = location.port
        @streamPort = 8080

        if info
            @host or= info.host
            @port or= info.port
            @streamPort or= info.streamPort

        @pressed = new Set()

        @sio = new WebSocket "ws://#{@host}:#{@port}/websocket"
        @sio.onmessage = (msg) =>
            data = JSON.parse msg.data
            if data[0] == 'position'
                @move data[1]

        @getMetadata (data) =>
            imageUrl = "http://#{@host}:#{@port}#{data.vector}"
            @overlay = new RobotOverlay imageUrl, [0, 0], data.size[1],
                                        data.size[0]
            @overlay.addTo map
            $(@overlay._image).click =>
                # notify of clicked robot action
                RobotActions.click @
                # don't propagate event
                false
            # fetch initial position
            # overlay needs to be already loaded
            @getOdometry (data) =>
                @move data

    move: (pos) ->
        RobotActions.move @, pos

    getSensor: (name, callback) ->
        @getRequest 'sensor', callback, name

    getOdometry: (callback) ->
        @getRequest 'odometry', callback

    getMetadata: (callback) ->
        @getRequest 'metadata', callback

    setPos: (x, y, theta, callback) ->
        @setRequest 'position', callback, x: x, y: y, theta: theta

    setPath: (path, callback) ->
        if path == undefined
            path = trajectory.getLatLngs().map (e) -> [e.lat, e.lng]

        @setRequest 'path', callback, path: JSON.stringify(path)

    postCommand: (command, callback) ->
        @setRequest 'text', callback, text: command

    setManual: (callback) ->
        @setRequest 'manual_mode', callback

        # add key handling events
        $(document.body).on 'keydown.robot', (e) =>
            # 87 -> W
            # 65 -> A
            # 83 -> S
            # 68 -> D

            # 81 -> Q
            # 69 -> E

            @pressed.add e.which if e.which in [87, 65, 83, 68, 81, 69]
            @sendKeys()

        $(document.body).on 'keyup.robot', (e) =>
            @pressed.delete e.which
            @sendKeys()

    sendKeys: ->
        if @manual
            l = []
            @pressed.forEach (e) -> l.push e
            data = JSON.stringify ['keys', l]
            @sio.send data

    setAuto: (callback) ->
        $(document.body).off 'keydown.robot'
        $(document.body).off 'keyup.robot'

        @setRequest 'auto_mode', callback


    # AJAX requests
    getRequest: (route, callback, param) ->
        request =
            url: "http://#{@host}:#{@port}/#{route}#{if param == undefined then ''\
                else "/#{param}"}"
            method: "GET"
            crossDomain: true

        $.ajax(request).done (data) ->
            if callback != undefined
                callback(data);

            if DEBUG
                for prop in data
                    console.log "result.#{prop} = #{data[prop]}"

    setRequest: (route, callback, param) ->
        request =
            url: "http://#{@host}:#{@port}/#{route}"
            method: "PUT"
            crossDomain: true
            data: param

        $.ajax(request).done (data) ->
            if callback != undefined
                callback.call(data)

            if DEBUG
                for prop in data
                    console.log "result.#{prop} = #{data[prop]}"


module.exports = Robot

# crazy hack!!, prevent dependency loop from actions/robot.coffee
# Robot requirement
RobotActions = require './actions/robot'
