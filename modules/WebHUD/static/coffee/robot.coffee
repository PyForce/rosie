# Class that wraps robot communication
class Robot

    constructor: (@overlay, @host) ->
        if @host == undefined
            @host = "#{document.domain}:#{location.port}"
        @manual = false

    move: (@pos) ->
        @overlay.setLatLng [@pos.x, @pos.y]
        @overlay.setAngle @pos.theta

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
        @manual = true
        @setRequest 'manual_mode', callback

    setAuto: (callback) ->
        @manual = false
        @setRequest 'auto_mode', callback


    # AJAX requests
    getRequest: (route, callback, param) ->
        request =
            url: "http://#{@host}/#{route}#{if param == undefined then ''\
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
            url: "http://#{@host}/#{route}"
            method: "PUT"
            crossDomain: true
            data: param

        $.ajax(request).done (data) ->
            if callback != undefined
                callback.call(data)

            if DEBUG
                for prop in data
                    console.log "result.#{prop} = #{data[prop]}"
